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

import deform
from deform.form import Button
from deform import widget

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
    return widget.RadioChoiceWidget(values = choices)

class SelectProcessSchema(colander.MappingSchema):
    description = "Select a workflow process for ESGF data"
    appstruct = {}

    process = colander.SchemaNode(
        colander.String(),
        widget = deferred_choose_workflow_widget)

# select data source schema
# -------------------------

class SelectDataSourceSchema(colander.MappingSchema):
    description = "Select data source"
    appstruct = {}
    choices = [('org.malleefowl.esgf.opendap', "ESGF OpenDAP"), ('org.malleefowl.esgf.wget', "ESGF wget")]

    data_source = colander.SchemaNode(
        colander.String(),
        missing = choices[0][0],
        widget = widget.RadioChoiceWidget(values = choices))

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

# esg aggregation schema
# ----------------

@colander.deferred
def deferred_esg_files_widget(node, kw):
    request = kw.get('request', None)
    wizard_state = kw.get('wizard_state', None)
    states = wizard_state.get_step_states()
    search_state = states.get(wizard_state.get_step_num() - 1)
    selection = search_state['selection']
    data_source_state = states.get(wizard_state.get_step_num() - 2)
    data_source = data_source_state['data_source']

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
        if data_source == 'org.malleefowl.esgf.opendap':
            agg_ctx = result.aggregation_context()
            for agg in agg_ctx.search():
                choices.append( (agg.opendap_url, agg.opendap_url) )
        else:
            file_ctx = result.file_context()
            for f in file_ctx.search():
                choices.append( (f.download_url, f.download_url) )
   
    return widget.RadioChoiceWidget(values=choices)

class EsgFilesSchema(colander.MappingSchema):
    description = 'You need to choose a single file url'
    appstruct = {}
    
    file_url = colander.SchemaNode(
        colander.String(),
        description = 'File URL',
        missing = '',
        widget = deferred_esg_files_widget)

# opendap schema
# --------------

def bind_esg_access_schema(node, kw):
    log.debug("bind access schema, kw=%s" % (kw))
    request = kw.get('request', None)
    wizard_state = kw.get('wizard_state', None)
    if request != None and wizard_state != None:
        states = wizard_state.get_step_states()
        data_source_state = states.get(wizard_state.get_step_num() - 3)
        identifier = data_source_state['data_source']
        wps = WebProcessingService(wps_url(request), verbose=False)
        process = wps.describeprocess(identifier)
        node.add_nodes(process)
    if node.get('file_url', False):
        del node['file_url']

# wps process schema
# ------------------

def bind_wps_schema(node, kw):
    log.debug("bind wps schema, kw=%s" % (kw))
    request = kw.get('request', None)
    wizard_state = kw.get('wizard_state', None)
    if request != None and wizard_state != None:
        states = wizard_state.get_step_states()
        state = states.get(0)
        identifier = state['process']
        wps = WebProcessingService(wps_url(request), verbose=False)
        process = wps.describeprocess(identifier)
        node.add_nodes(process)
    if node.get('file_url', False):
        del node['file_url']

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
        log.debug('calling schema.bind on schema=%s' % (schema))
        self.schema = schema.bind(request=request, wizard_state=self.wizard_state)
        log.debug('after wizard bind, schema = %s' % (self.schema))
        form_view.schema = self.schema
        buttons = []

        prev_disabled = False
        next_disabled = False

        if hasattr(self.schema, 'prev_ok'):
            prev_disabled = not self.schema.prev_ok(request)

        if hasattr(self.schema, 'next_ok'):
            next_disabled = not self.schema.next_ok(request)

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
        form_view.appstruct = getattr(self.schema, 'appstruct', None)
        log.debug("before form_view, schema = %s" % (self.schema))
        result = form_view()
        return result


class Done():
    form_view_class = FormView
    schema = SummarySchema(title="Summary")
    states = None
    
    def __init__(self):
        pass
    
    def __call__(self, request, states):
        wps = WebProcessingService(wps_url(request), verbose=True)
        
        sys_path = os.path.abspath(os.path.join(os.path.dirname(owslib.__file__), '..'))

        workflow_params = dict(sys_path = sys_path, service = wps.url)
        log.debug('states 1 = %s' % (states[1]))
        workflow_params['download_process'] = str(states[1].get('data_source'))
        workflow_params['openid'] = str(states[4].get('openid'))
        workflow_params['password'] = str(states[4].get('password'))
        workflow_params['file_url'] = str(states[3].get('file_url'))
        workflow_params['download_params'] = [
            ('startindex', int(states[4].get('startindex'))), 
            ('endindex', int(states[4].get('endindex')))]
        workflow_params['work_process'] = str(states[0].get('process'))
        workflow_params['work_params'] = states[5].items()
        workflow_template_filename = os.path.join(os.path.dirname(__file__), 'templates/wps/wps.yaml')
        workflow_template = Template(filename=workflow_template_filename)
        workflow_description = workflow_template.render(**workflow_params)

        identifier = 'org.malleefowl.restflow'
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
    schemas = []
    schemas.append( SelectProcessSchema(title='Select Process') )
    schemas.append( SelectDataSourceSchema(title='Select Data Source') )
    schemas.append( EsgSearchSchema(title='Select ESGF Dataset') )
    schemas.append( EsgFilesSchema(title='Select File URL') )
    schemas.append( WPSSchema(title='Access Parameters', 
                              after_bind=bind_esg_access_schema,
                              ))
    schemas.append( WPSSchema(title='Process Parameters', 
                              after_bind=bind_wps_schema,
                              ))

    wizard = FormWizard('Workflow', 
                        Done(), 
                        *schemas 
                        )
    view = MyFormWizardView(wizard)
    return view(request)


