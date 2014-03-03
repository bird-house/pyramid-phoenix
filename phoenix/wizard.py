# views.py
# Copyright (C) 2013 the ClimDaPs/Phoenix authors and contributors
# <see AUTHORS file>
#
# This module is part of ClimDaPs/Phoenix and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import os
import datetime
import json
import yaml

from pyramid.view import view_config, forbidden_view_config
from pyramid.httpexceptions import HTTPException, HTTPFound, HTTPNotFound
from pyramid.security import authenticated_userid
from pyramid_deform import FormView, FormWizard, FormWizardView

import deform
from deform.form import Button
from deform import widget

import colander
from colander import Range, Invalid, null

from mako.template import Template

from .models import (
    add_job, 
    )
from .helpers import (
    wps_url, 
    esgsearch_url,
    )
from .wps import WPSSchema

from .widget import (
    EsgSearchWidget,
    EsgFilesWidget,
    FileSearchWidget,
    WizardStatesWidget
    )

from owslib.wps import WebProcessingService, monitorExecution

import logging

log = logging.getLogger(__name__)

# select process schema
# ---------------------

@colander.deferred
def deferred_choose_workflow_widget(node, kw):
    request = kw.get('request')
    wps = WebProcessingService(wps_url(request), verbose=False, skip_caps=True)
    wps.getcapabilities()
    choices = []
    for process in wps.processes:
        if 'worker' in process.identifier:
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

@colander.deferred
def deferred_choose_datasource_widget(node, kw):
    request = kw.get('request')
    wps = WebProcessingService(wps_url(request), verbose=False, skip_caps=True)
    wps.getcapabilities()
    choices = []
    for process in wps.processes:
        if 'source' in process.identifier:
            choices.append( (process.identifier, process.title) )
    return widget.RadioChoiceWidget(values = choices)

class SelectDataSourceSchema(colander.MappingSchema):
    description = "Select data source"
    appstruct = {}

    data_source = colander.SchemaNode(
        colander.String(),
        widget = deferred_choose_datasource_widget)

# search schema
# -----------------

def search_metadata(url, wizard_state):
    if url == None or wizard_state == None:
        return {}
    
    states = wizard_state.get_step_states()
    process_state = states.get(0)
    processid = process_state['process']
    identifier = 'org.malleefowl.metadata'
    inputs = [("processid", str(processid))]
    outputs = [("output",False)]
    log.debug("wps url=%s", url)
    wps = WebProcessingService(url, verbose=False)
    execution = wps.execute(identifier, inputs=inputs, output=outputs)
    monitorExecution(execution)
    if len(execution.processOutputs) != 1:
        return
    output = execution.processOutputs[0]
    log.debug('output %s, data=%s, ref=%s', output.identifier, output.data, output.reference)
    if len(output.data) != 1:
        return {}
    metadata = json.loads(output.data[0])
    return metadata

def bind_search_schema(node, kw):
    log.debug("bind esg search schema, kw=%s" % (kw))
    request = kw.get('request', None)
    wizard_state = kw.get('wizard_state', None)
    if request == None or wizard_state == None:
        return

    states = wizard_state.get_step_states()
    data_source_state = states.get(1)
    data_source = data_source_state['data_source']

    metadata = search_metadata( wps_url(request), wizard_state)

    constraints =  metadata.get('esgfilter')
    log.debug('constraints = %s', constraints )
    query = metadata.get('esgquery')
    log.debug('query = %s', query )
    url = esgsearch_url(request)
    search = dict(facets=constraints, query=query)
    
    if 'esgf' in data_source:
        node.get('selection').title = 'ESGF Search'
        node.get('selection').default = json.dumps(search) 
        node.get('selection').widget = EsgSearchWidget(url=url)
    else:
        node.get('selection').title = 'Search Filter'
        node.get('selection').widget = FileSearchWidget()

    request.session['phoenix.wizard.files'] = None
    request.session.changed()


def esgsearch_validator(node, value):
    search = json.loads(value)
    if search.get('hit-count', 0) > 20:
        raise Invalid(node, 'More than 20 datasets selected: %r.' %  search['hit-count'])

class SearchSchema(colander.MappingSchema):
    description = 'Search Input Files'
    appstruct = {}

    selection = colander.SchemaNode(
        colander.String(),
        validator = esgsearch_validator
        )

    def next_ok(self, request):
        return True

# select files schema
# -------------------

def search_local_files(url, openid, filter):
    if url == None:
        return {}
    
    identifier = 'org.malleefowl.listfiles'
    inputs = [("openid", str(openid)), ("filter", str(filter))]
    outputs = [("output",False)]
    wps = WebProcessingService(url, verbose=False)
    execution = wps.execute(identifier, inputs=inputs, output=outputs)
    monitorExecution(execution)
    if len(execution.processOutputs) != 1:
        return
    output = execution.processOutputs[0]
    log.debug('output %s, data=%s, ref=%s', output.identifier, output.data, output.reference)
    if len(output.data) != 1:
        return {}
    files = json.loads(output.data[0])
    return files

def bind_files_schema(node, kw):
    from .models import user_openid
    
    request = kw.get('request', None)
    wizard_state = kw.get('wizard_state', None)

    if request == None or wizard_state == None:
        log.debug('not fetching files')
        return

    openid = user_openid(request, authenticated_userid(request))

    log.debug('step num = %s', wizard_state.get_step_num())

    states = wizard_state.get_step_states()
    
    data_source_state = states.get(1)
    data_source = data_source_state['data_source']

    search_state = states.get(2)
    search = json.loads( search_state['selection'])

    log.debug('fetching files')
    # TODO: cache results
    if 'esgf' in data_source:
        if 'opendap' in data_source:
            node.get('file_identifier').widget = EsgFilesWidget(
                url=esgsearch_url(request), search_type='Aggregation', search=search)
        else: # wget
            node.get('file_identifier').widget = EsgFilesWidget(
                url=esgsearch_url(request), search_type='File', search=search)
    elif 'filesystem' in data_source:
        choices = [(f, f) for f in search_local_files( wps_url(request), openid, search['filter'])]
        node.get('file_identifier').widget = widget.CheckboxChoiceWidget(values=choices)
    else:
        log.error('unknown datasource: %s', data_source)

   
class SelectFilesSchema(colander.MappingSchema):
    description = 'Choose input files'
    appstruct = {}
    
    file_identifier = colander.SchemaNode(
        colander.Set(),
        description = 'File Identifier',
        )

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
    if node.get('file_identifier', False):
        del node['file_identifier']

# wps process schema
# ------------------

def bind_wps_schema(node, kw):
    log.debug("bind wps schema, kw=%s" % (kw))
    request = kw.get('request', None)
    wizard_state = kw.get('wizard_state', None)
    
    if request == None or wizard_state == None:
        return
  
    states = wizard_state.get_step_states()
    state = states.get(0)
    identifier = state['process']
    wps = WebProcessingService(wps_url(request), verbose=False)
    process = wps.describeprocess(identifier)
   
    node.add_nodes(process)

    if node.get('file_identifier', False):
        del node['file_identifier']

# summary schema
# --------------
    
class SummarySchema(colander.MappingSchema):
    description = 'Summary'
    appstruct = {}

    states = colander.SchemaNode(
        colander.String(),
        title = 'States',
        missing = '',
        widget=WizardStatesWidget())

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
        cancel_disabled = False

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
        cancel_button = Button(name='cancel', title='Cancel',
                               disabled=cancel_disabled)

        if step > 0:
            buttons.append(prev_button)

        if step < len(self.wizard.schemas)-1:
            buttons.append(next_button)
        else:
            buttons.append(done_button)
        buttons.append(cancel_button)

        form_view.buttons = buttons
        form_view.next_success = self.next_success
        form_view.previous_success = self.previous_success
        form_view.previous_failure = self.previous_failure
        form_view.cancel_success = self.cancel
        form_view.cancel_failure = self.cancel
        form_view.show = self.show
        form_view.appstruct = getattr(self.schema, 'appstruct', None)
        log.debug("before form_view, schema = %s" % (self.schema))
        result = form_view()
        return result

    def cancel(self, validated):
        self.wizard_state.clear()
        return HTTPFound(location = self.request.path_url)


class Done():
    form_view_class = FormView
    schema = SummarySchema(title="Summary")
    states = None
    
    def __init__(self):
        pass
    
    def __call__(self, request, states):
        service = wps_url(request)
        source = dict(
            service = service,
            identifier = str(states[1].get('data_source')),
            input = [],
            output = ['output'],
            sources = map(lambda x: [str(x)], states[3].get('file_identifier')),
            )
        if states[4].has_key('openid'):
            source['input'].append('openid=' + str(states[4].get('openid', '')))
            source['input'].append('password=' + str(states[4].get('password', '')))
        if states[4].has_key('startindex'):
            source['input'].append('startindex=' + str(states[4].get('startindex', '')))
            source['input'].append('endindex=' + str(states[4].get('endindex', '')))
        if states[5].has_key('info_notes'):
            del(states[5]['info_notes'])
        if states[5].has_key('info_tags'):
            del(states[5]['info_tags'])
        worker = dict(
            service = service,
            identifier = str(states[0].get('process')),
            input = map(lambda x: str(x[0]) + '=' + str(x[1]), states[5].items()),
            output = ['output'])
        nodes = dict(source=source, worker=worker)
        log.debug( json.dumps(nodes) )

        # run workflow
        wps = WebProcessingService(service, verbose=True)

        # TODO: chain processes

        # get wf description
        identifier = 'org.malleefowl.restflow.generate'
        inputs = [("name", "simpleWorkflow"), ("nodes", json.dumps(nodes))]
        outputs = [("output",True)]
        execution = wps.execute(identifier, inputs=inputs, output=outputs)
        monitorExecution(execution, sleepSecs=1)
        wf_url = execution.processOutputs[0].reference

        log.debug('wf generated %s', wf_url)

        # run workflow
        identifier = 'org.malleefowl.restflow.run'
        inputs = [("workflow_description", wf_url)]
        outputs = [("output",True)]
        execution = wps.execute(identifier, inputs=inputs, output=outputs)

        log.debug('starting wf')
        
        add_job(
            request = request,
            user_id = authenticated_userid(request), 
            identifier = identifier, 
            wps_url = wps.url, 
            execution = execution,
            notes = states[5].get('info_notes', ''),
            tags = states[5].get('info_tags', ''))
        
        form_view = self.form_view_class(request)
        form_view.schema = self.schema.bind()
        self.states = states
        form_view.appstruct = self.appstruct 
        result = form_view()
        return result

    def appstruct(self):
        return {'states': "Job submitted"}

@view_config(route_name='wizard',
             renderer='templates/wizard.pt',
             layout='default',
             permission='edit',
             )
def wizard(request):
    schemas = []
    schemas.append( SelectProcessSchema(title='Select Process') )
    schemas.append( SelectDataSourceSchema(title='Select Data Source') )
    schemas.append( SearchSchema(
        title='Search Input Files',
        after_bind=bind_search_schema,
        ))
    schemas.append( SelectFilesSchema(
        title='Select Files',
        after_bind=bind_files_schema,) )
    schemas.append( WPSSchema(
        title='Access Parameters', 
        after_bind=bind_esg_access_schema,
        ))
    schemas.append( WPSSchema(
        info=True,
        title='Process Parameters', 
        after_bind=bind_wps_schema,
        ))

    wizard = FormWizard('Workflow', 
                        Done(), 
                        *schemas 
                        )
    view = MyFormWizardView(wizard)
    return view(request)


