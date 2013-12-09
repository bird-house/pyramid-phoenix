# schema.py
# Copyright (C) 2013 the ClimDaPs/Phoenix authors and contributors
# <see AUTHORS file>
#
# This module is part of ClimDaPs/Phoenix and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php


import colander
import deform
from deform.widget import OptGroup

import logging

log = logging.getLogger(__name__)


from owslib.wps import WebProcessingService
from .helpers import wps_url
from pyramid.security import has_permission


# process list
# ------------

@colander.deferred
def deferred_select_process_widget(node, kw):
    request = kw.get('request')
    log.debug('current wps for proccess: %s' % (wps_url(request)))
    wps = WebProcessingService(wps_url(request), verbose=False, skip_caps=True)
    wps.getcapabilities()

    test_group = []
    csc_group = []
    dkrz_group = []
    base_group = []
    c3grid_group = []
    other_group = []
    for process in wps.processes:
        if 'test' in process.identifier:
            test_group.append( (process.identifier, process.title) )
        elif 'de.csc' in process.identifier:
            csc_group.append( (process.identifier, process.title) )
        elif 'de.dkrz' in process.identifier:
            dkrz_group.append( (process.identifier, process.title) )
        elif 'org.malleefowl' in process.identifier:
            base_group.append( (process.identifier, process.title) )
        elif 'de.c3grid' in process.identifier:
            c3grid_group.append( (process.identifier, process.title) )
        else:
            other_group.append( (process.identifier, process.title) )
    choices = [ ('', 'Select Process') ]
    if has_permission('admin', request.context, request) and len(base_group) > 0:
        choices.append( OptGroup('Base', *base_group) )
    if len(test_group) > 0:
        choices.append( OptGroup('Test', *test_group) )
    if len(c3grid_group) > 0:
        choices.append( OptGroup('C3Grid', *c3grid_group) )
    if len(csc_group) > 0:
        choices.append( OptGroup('CSC', *csc_group) )
    if len(dkrz_group) > 0:
        choices.append( OptGroup('DKRZ', *dkrz_group) )
    if len(other_group) > 0:
        choices.append( OptGroup('Other', *other_group) )
    
    return deform.widget.SelectWidget(
        values = choices,
        long_label_generator = lambda group, label: ' - '.join((group, label))
        )

class ProcessSchema(colander.MappingSchema):
    process = colander.SchemaNode(
        colander.String(),
        title = "WPS Process",
        widget = deferred_select_process_widget)

# admin
# -----

class AdminSchema(colander.MappingSchema):
    jobs_count = colander.SchemaNode(
        colander.Int(),
        name = 'jobs_count',
        title = "Number of Jobs",
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

    new_wps = colander.SchemaNode(
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

@colander.deferred
def deferred_job_widget(node, kw):
    request = kw.get('request')
    from .models import jobs_information 
    jobs = jobs_information(request)
    from .widget import JobsWidget
    return JobsWidget(jobs = jobs)

    

class JobsSchema(colander.MappingSchema):
    process = colander.SchemaNode(
        colander.String(),
        title = "Jobs",
        missing=unicode(''),
        widget = deferred_job_widget
        )

