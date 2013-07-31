# schema.py
# Copyright (C) 2013 the ClimDaPs/Phoenix authors and contributors
# <see AUTHORS file>
#
# This module is part of ClimDaPs/Phoenix and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php


import colander
import deform

import logging

log = logging.getLogger(__name__)


from owslib.wps import WebProcessingService
from .helpers import wps_url

# esg search schema
# ------------------

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

class EsgSearchSchema(colander.MappingSchema):
    name = "Select ESGF Dataset"
    description = 'You need to choose a single dataset'
    is_esgsearch = True
    appstruct = {}

    opendap_url = colander.SchemaNode(
        colander.String(),
        description = 'OpenDAP Access URL',
        missing = '',
        widget = deferred_esgsearch_opendap_widget)

# workflow wizard
# ---------------

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

class ChooseWorkflowSchema(colander.MappingSchema):
    name = "Select Workflow Process"
    description = "Select a workflow process for ESGF data"
    is_esgsearch = False
    appstruct = {}

    workflow = colander.SchemaNode(
        colander.String(),
        widget = deferred_choose_workflow_widget)


# admin
# -----

class AdminSchema(colander.MappingSchema):
    history_count = colander.SchemaNode(
        colander.Int(),
        name = 'history_count',
        title = "Number of Processings",
        missing = 0,
        widget = deform.widget.TextInputWidget(readonly=True)
        )

# catalog
# -------

@colander.deferred
def deferred_wps_list_widget(node, kw):
    wps_list = kw.get('wps_list', [])
    readonly = kw.get('readonly', False)
    return deform.widget.RadioChoiceWidget(
        values=wps_list,
        readonly=readonly)

class CatalogAddWPSSchema(colander.MappingSchema):
    current_wps = colander.SchemaNode(
        colander.String(),
        title = "WPS List",
        description = 'List of known WPS',
        missing = '',
        widget=deferred_wps_list_widget)

    wps_url = colander.SchemaNode(
        colander.String(),
        title = 'WPS URL',
        description = 'Add new WPS URL',
        missing = '',
        default = '',
        validator = colander.url,
        widget = deform.widget.TextInputWidget())

class CatalogSelectWPSSchema(colander.MappingSchema):
   
    active_wps = colander.SchemaNode(
        colander.String(),
        title = 'WPS',
        description = "Select active WPS",
        widget = deferred_wps_list_widget
        )


      

    
