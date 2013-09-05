# models.py
# Copyright (C) 2013 the ClimDaPs/Phoenix authors and contributors
# <see AUTHORS file>
#
# This module is part of ClimDaPs/Phoenix and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

# TODO: refactor usage of mongodb etc ...

import uuid
import datetime

from pyesgf.search import SearchConnection

import logging

log = logging.getLogger(__name__)

from .helpers import mongodb_conn, esgsearch_url

# mongodb ...
# -----------

def database(request):
    conn = mongodb_conn(request)
    return conn.phoenix_db

def add_job(request, user_id, identifier, wps_url, execution):
    db = database(request)
    db.jobs.save(dict(
        user_id= user_id, 
        uuid=uuid.uuid4().get_hex(),
        identifier=identifier,
        service_url=wps_url,
        status_location=execution.statusLocation,
        status = execution.status,
        start_time = datetime.datetime.now(),
        end_time = datetime.datetime.now(),
    ))
    log.debug('count jobs = %s', db.jobs.count())

def get_job(request, uuid):
    db = database(request)
    job = db.jobs.find_one({'uuid': uuid})
    return job

def update_job(request, job):
    db = database(request)
    db.jobs.update({'uuid': job['uuid']}, job)

def num_jobs(request):
    db = database(request)
    return db.jobs.count()

def drop_jobs(request):
    db = database(request)
    db.jobs.drop()

def jobs_by_userid(request, user_id):
    db = database(request)
    return db.jobs.find( dict(user_id=user_id) )


# esgf search ....
# ----------------

def esgf_search_conn(request):
    return SearchConnection(esgsearch_url(request), distrib=False)
    
def esgf_search_context(request, query='*'):
    conn = esgf_search_conn(request)
    ctx = conn.new_context(project='CMIP5', latest=True, query=query)
    return ctx

def esgf_aggregation_search(ctx):
    log.debug("datasets found = %d", ctx.hit_count)
    result = ctx.search()[0]
    
    agg_ctx = result.aggregation_context()
    log.debug('opendap num files = %d', agg_ctx.hit_count)
    aggregations = []
    for agg in agg_ctx.search():
        # filter with selected variables
        ok = False
        for var_name in ctx.facet_constraints.getall('variable'):
            if var_name in agg.json.get('variable', []):
                ok = True
                break
        if not ok: continue

        aggregations.append( (agg.opendap_url, agg.aggregation_id) )
    return aggregations

def esgf_file_search(ctx, start, end):
    start_str = '%04d%02d%02d' % (start.year, start.month, start.day)
    end_str = '%04d%02d%02d' % (end.year, end.month, end.day)

    log.debug("filter from=%s, to=%s", start_str, end_str)
    
    log.debug("datasets found = %d", ctx.hit_count)
    result = ctx.search()[0]
    file_ctx = result.file_context()
    log.debug("files found = %d", file_ctx.hit_count)

    query_dict = dict()
    query_dict['type'] = 'File'
    query_dict['dataset_id'] = file_ctx.facet_constraints['dataset_id']
    if ctx.facet_constraints.has_key('variable'):
        query_dict['variable'] = ctx.facet_constraints['variable']
    
    response = ctx.connection.send_search(limit=file_ctx.hit_count, query_dict=query_dict)
    docs = response['response']['docs']
    files = []
    for doc in docs:
        download_url = None
        for encoded in doc['url']:
            url, mime_type, service = encoded.split('|')
            if 'HTTPServer' in service:
                download_url = url
                break
        if download_url == None:
            continue
        filename = doc['title']

        # filter with time constraint
        index = filename.rindex('-')
        f_start = filename[index-8:index]
        f_end = filename[index+1:index+9]
        if f_start >= start_str and f_end <= end_str:
            files.append( (download_url, filename) )
    return files
