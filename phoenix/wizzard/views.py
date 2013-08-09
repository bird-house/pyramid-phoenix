# views.py
# Copyright (C) 2013 the ClimDaPs/Phoenix authors and contributors
# <see AUTHORS file>
#
# This module is part of ClimDaPs/Phoenix and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import os

from pyramid.view import view_config, forbidden_view_config
from pyramid.httpexceptions import HTTPException, HTTPFound, HTTPNotFound
from pyramid.security import authenticated_userid
from pyramid_deform import FormView, FormWizard, FormWizardView
from deform.form import Button

from owslib.wps import WebProcessingService

from phoenix.models import esgf_search_context, add_job

from phoenix.helpers import wps_url


import logging

log = logging.getLogger(__name__)


class EsgSearchView(FormView):
    schema = None

    def submit_success(self, appstruct):
        opendap_url = appstruct['opendap_url']
        log.debug("submit result = %s", appstruct)
        #self.request.session.flash(u"Your changes have been saved.")
        return HTTPFound(location = self.request.route_url('admin'))

    def appstruct(self):
        return None


# workflow
# --------

class WorkflowFormWizard(FormWizard):
    pass
         
class WorkflowFormWizardView(FormWizardView):
    form_view_class = EsgSearchView
    ctx = None
    facet = None
    item = None
    constraints = None

    def __call__(self, request):
        self.request = request
        self.wizard_state = self.wizard_state_class(request, self.wizard.name)
        step = self.wizard_state.get_step_num()

        log.debug('step = %s', step)
        
        process = None

        if step > len(self.wizard.schemas)-1:
            states = self.wizard_state.get_step_states()
            result = self.wizard.done(request, states)
            self.wizard_state.clear()
            return result

        schema = self.wizard.schemas[step]
        
        if step == 2:
            states = self.wizard_state.get_step_states()
            state = self.deserialize(states[1])
            schema.appstruct['opendap_url'] = state['opendap_url']
        elif step == 3:
            states = self.wizard_state.get_step_states()
            wps = WebProcessingService(wps_url(self.request), verbose=True)
            state = self.deserialize(states[0])
            identifier = state['process']
            process = wps.describeprocess(identifier)
            log.debug('identifier = %s', identifier)
            schema = schema.__class__(process=process)

        form_view = self.form_view_class(request)
        log.debug('process = %s', process)
        self.schema = schema.bind(request=request, ctx=self.ctx)
        log.debug('num schema children = %s', len(self.schema.children))
        form_view.schema = self.schema
        buttons = []

        prev_disabled = False
        next_disabled = False

        if hasattr(schema, 'prev_ok'):
            prev_disabled = not schema.prev_ok(request)

        if hasattr(schema, 'next_ok'):
            next_disabled = not schema.next_ok(request)

        prev_button = Button(name='previous', title='Previous',
                             disabled=prev_disabled)
        next_button = Button(name='next', title='Next',
                             disabled=next_disabled)
        done_button = Button(name='next', title='Done',
                             disabled=next_disabled)

        if step > 0:
            buttons.append(prev_button)

        if step < len(self.wizard.schemas)-1:
            buttons.append(next_button)
        else:
            buttons.append(done_button)

        form_view.buttons = buttons
        form_view.next_success = self.next_success
        form_view.previous_success = self.previous_success
        form_view.previous_failure = self.previous_failure
        form_view.show = self.show
        form_view.appstruct = getattr(schema, 'appstruct', None)

        result = form_view()
        return result

    def show(self, form):
        is_esgsearch = getattr(self.schema, 'is_esgsearch', False)
        appstruct = getattr(self.schema, 'appstruct', None)

        state = self.wizard_state.get_step_state(appstruct)
        state = self.deserialize(state)
        result = dict(form=form.render(appstruct=state))

        log.debug('title=%s, description=%s', self.schema.title, self.schema.description)

        result.update(
        dict(
            title=self.schema.title,
            description=self.schema.description,
            is_esgsearch=is_esgsearch,
            ctx=self.ctx,
            constraints=self.constraints,
            facet=self.facet,
            item=self.item)
        )
        return result

class Workflow(object):
    pass

def workflow_wizard_done(request, states):
    from mako.template import Template

    log.debug('states = %s', states)
    #wizard.get_summary(request)

    wps = WebProcessingService(wps_url(request), verbose=True)
    identifier = 'de.dkrz.restflow.run'
    workflow_template_filename = os.path.join(os.path.abspath(os.curdir), 'phoenix/wps/templates/wps.yaml')
    workflow_template = Template(filename=workflow_template_filename)
    workflow_description = workflow_template.render(
        service = wps.url,
        process = states[0].get('process'),
        openid = states[2].get('openid'),
        password = states[2].get('password'),
        opendap_url = states[2].get('opendap_url')
        )
    #log.debug("workflow_description = %s", workflow_description)
    inputs = [("workflow_description", str(workflow_description))]
    outputs = [("output",True)]
    execution = wps.execute(identifier, inputs=inputs, output=outputs)

    add_job(
        request = request,
        user_id = authenticated_userid(request), 
        identifier = identifier, 
        wps_url = wps.url, 
        execution = execution)

    return {
        'form' : FormView(request),
        'title': 'Summary',
        'description': '...',
        'is_esgsearch': False 
        }

@view_config(route_name='wizzard',
             renderer='templates/wizzard.pt',
             layout='default',
             permission='edit',
             )
def wizard(request):
    ctx = esgf_search_context(request)

    all_facets = ctx.facet_counts.keys()

    action = request.matchdict.get('action', 'update')
    facet = request.matchdict.get('facet', None)
    item = request.matchdict.get('item', None)
    constraints = {}
    for (key,value) in request.params.iteritems():
        if not key in all_facets:
            continue
        constraints[key] = value
    
    log.debug('facet=%s, item=%s, action=%s', facet, item, action)
    log.debug('constraints=%s', constraints)

    if action == 'update':
        pass
    elif action == 'add':
        constraints[facet] = item
    elif action == 'delete':
        del constraints[facet]

    ctx = ctx.constrain(**constraints)
    
    # choose wps
    from .schema import SelectProcessSchema
    schema_select_process = SelectProcessSchema(title='Select Process')

    from .schema import TestSearchSchema
    schema_esgsearch = TestSearchSchema(title="Test Search Schema")

    # select esgf dataset
    from .schema import EsgSearchSchema
    #schema_esgsearch = EsgSearchSchema(title='Select ESGF Dataset')

    # select files
    #from .schema import EsgFilesSchema
    #schema_esgfiles = EsgFilesSchema(title='Select ESGF File')

    # wget process
    from phoenix.wps.schema import WPSInputSchemaNode
    wps = WebProcessingService(wps_url(request), verbose=True)
    process = wps.describeprocess('de.dkrz.esgf.wget')
    schema_wget = WPSInputSchemaNode(process=process)

    process = wps.describeprocess('de.dkrz.esgf.opendap')
    schema_opendap = WPSInputSchemaNode(process=process)

    # get wps process params
    schema_process = WPSInputSchemaNode()

    wizard = WorkflowFormWizard('Workflow', 
                                workflow_wizard_done, 
                                schema_select_process, 
                                schema_esgsearch,
                                #schema_esgfiles,
                                #schema_wget,
                                schema_opendap,
                                schema_process)
    view = WorkflowFormWizardView(wizard)
    view.ctx = ctx
    view.facet = facet
    view.item = item
    view.constraints = constraints
    return view(request)


