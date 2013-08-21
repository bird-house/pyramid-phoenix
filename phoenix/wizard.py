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
import deform

import colander

import owslib
from owslib.wps import WebProcessingService

from mako.template import Template

from .models import add_job, esgf_search_context
from .helpers import wps_url, esgsearch_url
from .wps import WPSSchema

import logging

log = logging.getLogger(__name__)


from owslib.wps import WebProcessingService
from phoenix.helpers import wps_url
from phoenix.widget import EsgSearchWidget, EsgFilesWidget

from pyesgf.search import SearchConnection

# select process schema
# ---------------------

@colander.deferred
def deferred_choose_workflow_widget(node, kw):
    request = kw.get('request')
    wps = WebProcessingService(wps_url(request), verbose=False, skip_caps=True)
    wps.getcapabilities()
    choices = []
    for process in wps.processes:
        if '_workflow' in process.identifier:
            choices.append( (process.identifier, process.title) )
    return deform.widget.SelectWidget(values = choices)

class SelectProcessSchema(colander.MappingSchema):
    description = "Select a workflow process for ESGF data"
    appstruct = {}

    process = colander.SchemaNode(
        colander.String(),
        widget = deferred_choose_workflow_widget)

# esg search schema
# -----------------

@colander.deferred
def deferred_esgsearch_widget(node, kw):
    request = kw.get('request')
    url = esgsearch_url(request)
    return EsgSearchWidget(url=url)
    
class EsgSearchSchema(colander.MappingSchema):
    description = 'Choose a single Dataset'
    appstruct = {}

    selection = colander.SchemaNode(
        colander.String(),
        title = 'Current Selection',
        missing = '',
        widget = deferred_esgsearch_widget)

# esg files schema
# ----------------

@colander.deferred
def deferred_esgfiles_widget(node, kw):
    request = kw.get('request', None)
    wizard_state = kw.get('wizard_state', None)
    states = wizard_state.get_step_states()
    state = states.get(wizard_state.get_step_num() - 1)
    selection = state['selection']

    ctx = esgf_search_context(request)
    constraints = {}
    for constraint in selection.split(','):
        if ':' in constraint:
            key,value = constraint.split(':')
            constraints[key] = value
    ctx = ctx.constrain(**constraints) 
    
    choices = []

    if ctx.hit_count == 1:
        result = ctx.search()[0]
        agg_ctx = result.aggregation_context()
        for agg in agg_ctx.search():
            choices.append( (agg.opendap_url, agg.opendap_url) )
   
    return deform.widget.RadioChoiceWidget(
        values=choices)

    
class EsgFilesSchema(colander.MappingSchema):
    description = 'You need to choose a single file'
    appstruct = {}
    
    opendap_url = colander.SchemaNode(
        colander.String(),
        description = 'OpenDAP Access URL',
        missing = '',
        widget = deferred_esgfiles_widget)


# opendap schema
# --------------

class OpendapSchemaAdaptor(WPSSchema):
    def __init__(self, process=None, unknown='ignore', **kw):
        WPSSchema.__init__(self, process, unknown, **kw)
        # TODO: avoid hard coded wps parameters
        if self.get('opendap_url') != None:
            self.__delitem__('opendap_url')

# wps process schema
# ------------------

class ProcessSchemaAdaptor(WPSSchema):
    def __init__(self, process=None, unknown='ignore', **kw):
        WPSSchema.__init__(self, process, unknown, **kw)
        # TODO: avoid hard coded wps parameters
        if self.get('netcdf') != None:
            self.__delitem__('netcdf')

# summary schema
# --------------
    
class SummarySchema(colander.MappingSchema):
    description = 'Summary'
    appstruct = {}

    states = colander.SchemaNode(
        colander.String(),
        title = 'States',
        missing = '')

# wizard
# ------

class MyFormWizardView(FormWizardView):
    def __call__(self, request):
        self.request = request
        self.wizard_state = self.wizard_state_class(request, self.wizard.name)
        step = self.wizard_state.get_step_num()

        if step > len(self.wizard.schemas)-1:
            states = self.wizard_state.get_step_states()
            result = self.wizard.done(request, states)
            self.wizard_state.clear()
            return result
        form_view = self.form_view_class(request)
        schema = self.wizard.schemas[step]
        self.schema = schema.bind(request=request, wizard_state=self.wizard_state)
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


class Done():
    form_view_class = FormView
    schema = SummarySchema(title="Summary")
    states = None
    
    def __init__(self):
        pass
    
    def __call__(self, request, states):
        log.debug('opendap_url = %s' % (states[1].get('opendap_url')))

        sys_path = os.path.abspath(os.path.join(os.path.dirname(owslib.__file__), '..'))
        
        wps = WebProcessingService(wps_url(request), verbose=True)
        identifier = 'de.dkrz.restflow.run'
        workflow_template_filename = os.path.join(os.path.abspath(os.curdir), 'phoenix/templates/wps/wps.yaml')
        workflow_template = Template(filename=workflow_template_filename)
        workflow_description = workflow_template.render(
            sys_path = sys_path,
            service = wps.url,
            process = states[0].get('process'),
            openid = states[3].get('openid'),
            password = states[3].get('password'),
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
        
        form_view = self.form_view_class(request)
        form_view.schema = self.schema.bind()
        self.states = states
        form_view.appstruct = self.appstruct 
        result = form_view()
        return result

    def appstruct(self):
        return {'states': str(self.states)}

@view_config(route_name='wizard',
             renderer='templates/wizard.pt',
             layout='default',
             permission='edit',
             )
def wizard(request):
    # choose process
    schema_select_process = SelectProcessSchema(title='Select Process')

    # select esgf dataset
    schema_esgsearch = EsgSearchSchema(title='Select ESGF Dataset')

    # select files
    schema_esgfiles = EsgFilesSchema(title='Select ESGF File')

    # wget process
    wps = WebProcessingService(wps_url(request), verbose=True)
    #process = wps.describeprocess('de.dkrz.esgf.wget')
    #schema_wget = WPSInputSchemaNode(process=process)

    process = wps.describeprocess('de.dkrz.esgf.opendap')
    schema_opendap = OpendapSchemaAdaptor(process=process)

    process = wps.describeprocess('de.dkrz.cdo.sinfo_workflow')
    schema_process = ProcessSchemaAdaptor(process=process)

    wizard = FormWizard('Workflow', 
                        Done(), 
                        schema_select_process, 
                        schema_esgsearch,
                        schema_esgfiles,
                        schema_opendap,
                        schema_process,
                        )
    view = MyFormWizardView(wizard)
    return view(request)


