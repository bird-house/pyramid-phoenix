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

import colander

from owslib.wps import WebProcessingService

from phoenix.models import add_job
from phoenix.helpers import wps_url


import logging

log = logging.getLogger(__name__)


class ResultSchema(colander.MappingSchema):
    description = 'Result'
    appstruct = {}

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
             renderer='../templates/wizzard.pt',
             layout='default',
             permission='edit',
             )
def wizard(request):
    # choose process
    from .schema import SelectProcessSchema
    schema_select_process = SelectProcessSchema(title='Select Process')

    # select esgf dataset
    from .schema import EsgSearchSchema
    schema_esgsearch = EsgSearchSchema(title='Select ESGF Dataset')

    # select files
    #from .schema import EsgFilesSchema
    #schema_esgfiles = EsgFilesSchema(title='Select ESGF File')

    # wget process
    #from phoenix.wps.schema import WPSInputSchemaNode
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


