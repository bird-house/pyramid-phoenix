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
from phoenix.widget import EsgSearchWidget

class EsgSearchSchema(colander.MappingSchema):
    description = 'Choose a single Dataset'
    appstruct = {}

    selection = colander.SchemaNode(
        colander.String(),
        title = 'Current Selection',
        missing = '',
        widget = EsgSearchWidget())

@colander.deferred
def deferred_esgsearch_opendap_widget(node, kw):
    ctx = kw.get('ctx')
   
    choices = []
    if ctx.hit_count == 1:
        result = ctx.search()[0]
        agg_ctx = result.aggregation_context()
        for agg in agg_ctx.search():
            choices.append( (agg.opendap_url, agg.opendap_url) )
   
    return deform.widget.SelectWidget(values = choices)

@colander.deferred
def deferred_esgsearch_files_widget(node, kw):
    ctx = kw.get('ctx')
   
    choices = []
    if ctx.hit_count == 1:
        result = ctx.search()[0]
        file_ctx = result.file_context()
        for my_file in file_ctx.search():
            choices.append( (my_file.download_url, my_file.download_url) )
   
    return deform.widget.SelectWidget(values = choices)

class EsgFilesSchema(colander.MappingSchema):
    description = 'You need to choose a single file'
    is_esgsearch = False
    appstruct = {}

    opendap_url = colander.SchemaNode(
        colander.String(),
        description = 'OpenDAP Access URL',
        missing = '',
        widget = deferred_esgsearch_opendap_widget)

    files_url = colander.SchemaNode(
        colander.String(),
        description = 'Files Access URL',
        missing = '',
        widget = deferred_esgsearch_files_widget)

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
    is_esgsearch = False
    appstruct = {}

    process = colander.SchemaNode(
        colander.String(),
        widget = deferred_choose_workflow_widget)

class ResultSchema(colander.MappingSchema):
    description = 'Result'
    appstruct = {}


# views
# -----
    
def done(request, states):
    form_view_class = FormView
    
    form_view = form_view_class(request)
    schema = ResultSchema()
    form_view.schema = schema.bind()
    result = form_view()
    return result

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

@view_config(route_name='wizzard',
             renderer='templates/wizzard.pt',
             layout='default',
             permission='edit',
             )
def wizard(request):
    # choose process
    schema_select_process = SelectProcessSchema(title='Select Process')

    # select esgf dataset
    schema_esgsearch = EsgSearchSchema(title='Select ESGF Dataset')

    # select files
    #schema_esgfiles = EsgFilesSchema(title='Select ESGF File')

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
                        done, 
                        schema_select_process, 
                        schema_esgsearch,
                        )
    view = FormWizardView(wizard)
    return view(request)


