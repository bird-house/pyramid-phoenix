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

from owslib.wps import WebProcessingService

from .models import add_job
from .helpers import wps_url

import logging

log = logging.getLogger(__name__)


# schema
# ------

from owslib.wps import WebProcessingService
from phoenix.helpers import wps_url
from phoenix.widget import EsgSearchWidget, EsgFilesWidget

# select process schema

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
    
class EsgSearchSchema(colander.MappingSchema):
    description = 'Choose a single Dataset'
    appstruct = {}

    selection = colander.SchemaNode(
        colander.String(),
        title = 'Current Selection',
        missing = '',
        widget = EsgSearchWidget())

# esg files schema
    
class EsgFilesSchema(colander.MappingSchema):
    description = 'You need to choose a single file'
    appstruct = {}
   
    opendap_url = colander.SchemaNode(
        colander.String(),
        description = 'OpenDAP Access URL',
        missing = '',
        widget = EsgFilesWidget())

# summary schema
    
class SummarySchema(colander.MappingSchema):
    description = 'Summary'
    appstruct = {}

    states = colander.SchemaNode(
        colander.String(),
        title = 'States',
        missing = '')

# views
# -----

class Done():
    form_view_class = FormView
    schema = SummarySchema(title="Summary")
    states = None
    
    def __init__(self):
        pass
    
    def __call__(self, request, states):
        form_view = self.form_view_class(request)
        form_view.schema = self.schema.bind()
        self.states = states
        form_view.appstruct = self.appstruct 
        result = form_view()
        return result

    def appstruct(self):
        return {'states': str(self.states)}

def done_with_restflow(request, states):
    from mako.template import Template

    log.debug('states = %s', states)

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
        }

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
    #from .wps.schema import WPSInputSchemaNode
    #wps = WebProcessingService(wps_url(request), verbose=True)
    #process = wps.describeprocess('de.dkrz.esgf.wget')
    #schema_wget = WPSInputSchemaNode(process=process)

    #process = wps.describeprocess('de.dkrz.esgf.opendap')
    #schema_opendap = WPSInputSchemaNode(process=process)

    # get wps process params
    #schema_process = WPSInputSchemaNode()

    wizard = FormWizard('Workflow', 
                        Done(), 
                        schema_select_process, 
                        schema_esgsearch,
                        schema_esgfiles,
                        )
    view = FormWizardView(wizard)
    return view(request)


