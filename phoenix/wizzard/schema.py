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
from phoenix.helpers import wps_url
from phoenix.widget import EsgSearchWidget

class EsgSearchSchema(colander.MappingSchema):
    description = 'Choose a single Dataset'
    appstruct = {}

    search_filter = colander.SchemaNode(
        colander.String(),
        description = 'Search Filter',
        missing = '',
        widget = EsgSearchWidget())

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

class SelectProcessSchema(colander.MappingSchema):
    description = "Select a workflow process for ESGF data"
    is_esgsearch = False
    appstruct = {}

    process = colander.SchemaNode(
        colander.String(),
        widget = deferred_choose_workflow_widget)

