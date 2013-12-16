# models.py
# Copyright (C) 2013 the ClimDaPs/Phoenix authors and contributors
# <see AUTHORS file>
#
# This module is part of ClimDaPs/Phoenix and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

# TODO: refactor usage of mongodb etc ...

from pyramid.security import authenticated_userid

from pyramid.security import (
    Allow,
    Everyone,
    )

import uuid
import datetime

from pyesgf.search import SearchConnection
from pyesgf.multidict import MultiDict

import logging

log = logging.getLogger(__name__)

from .helpers import mongodb_conn, esgsearch_url

# mongodb ...
# -----------

def database(request):
    conn = mongodb_conn(request)
    return conn.phoenix_db

# registered users (whitelist)

def register_user(request, user_id,
                  name=None,
                  organisation=None,
                  notes=None,
                  activated=True):
    db = database(request)
    db.users.save(dict(
        user_id = user_id,
        name = name,
        organisation = organisation,
        notes = notes,
        activated = activated,
        ))


def unregister_user(request, user_id):
    db = database(request)
    db.users.remove(dict(user_id = user_id))

def activate_user(request, user_id):
    update_user(request, user_id, activated=True)

def deactivate_user(request, user_id):
    update_user(request, user_id, activated=False)

def update_user(request, user_id, activated=False):
    db = database(request)
    user = db.users.find_one(dict(user_id = user_id))
    user['activated'] = activated
    db.users.update(dict(user_id = user_id), user)

def all_users(request):
    db = database(request)
    return db.users.find()

def activated_users(request):
    db = database(request)
    return db.users.find(dict(activated = True))

def deactivated_users(request):
    db = database(request)
    return db.users.find(dict(activated = False))

# jobs ...

def add_job(request,
            identifier,
            wps_url,
            execution,
            user_id='anonymous',
            notes='',
            tags=''):
    db = database(request)
    db.jobs.save(dict(
        user_id = user_id, 
        uuid = uuid.uuid4().get_hex(),
        identifier = identifier,
        service_url = wps_url,
        status_location = execution.statusLocation,
        status = execution.status,
        start_time = datetime.datetime.now(),
        end_time = datetime.datetime.now(),
        notes = notes,
        tags = tags,
        ))
    #log.debug('count jobs = %s', db.jobs.count())

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

def jobs_by_userid(request, user_id='anonymous'):
    db = database(request)
    return db.jobs.find( dict(user_id=user_id) )

def drop_user_jobs(request):
    db = database(request)
    for job in jobs_by_userid(request, user_id=authenticated_userid(request)):
        db.jobs.remove({"uuid": job['uuid']})

def drop_jobs_by_uuid(request, uuids=[]):
    db = database(request)
    for uuid in uuids:
        db.jobs.remove({"uuid": uuid})


def jobs_information(request,sortkey="starttime",inverted=True):
    from owslib.wps import WebProcessingService, WPSExecution

    dateformat = '%a, %d %b %Y %I:%M:%S %p'
    jobs = []
    for job in jobs_by_userid(request, user_id=authenticated_userid(request)):

        job['starttime'] = job['start_time'].strftime(dateformat)

        # TODO: handle different process status
        if job['status'] in ['ProcessAccepted', 'ProcessStarted', 'ProcessPaused']:
            job['errors'] = []
            try:
                wps = WebProcessingService(job['service_url'], verbose=False)
                execution = WPSExecution(url=wps.url)
                execution.checkStatus(url=job['status_location'], sleepSecs=0)
                job['status'] = execution.status
                job['percent_completed'] = execution.percentCompleted
                job['status_message'] = execution.statusMessage
                job['error_message'] = ''
                for err in execution.errors:
                    job['errors'].append( dict(code=err.code, locator=err.locator, text=err.text) )
               
            except:
                msg = 'could not access wps %s' % (job['status_location'])
                log.warn(msg)
                job['status'] = 'Exception'
                job['errors'].append( dict(code='', locator='', text=msg) )
            
            job['end_time'] = datetime.datetime.now()
            for err in job['errors']:
                job['error_message'] = err.get('text', '') + ';'

            # TODO: configure output delete time
            dd = 3
            job['output_delete_time'] = datetime.datetime.now() + datetime.timedelta(days=dd)
            job['duration'] = str(job['end_time'] - job['start_time'])
            update_job(request, job)
        jobs.append(job)
    #sort the jobs by starttime
    if (sortkey == "starttime"):
        jobs = sorted(jobs, key=lambda job: datetime.datetime.strptime(job['starttime'], dateformat))
    else:
        jobs = sorted(jobs, key=lambda job: job[sortkey])
    #reverse the sorting
    if(inverted):
        jobs = jobs[::-1]
        
    return jobs

# esgf search ....
# ----------------

def esgf_search_conn(request, distrib=True):
    return SearchConnection(esgsearch_url(request), distrib=distrib)
    
def esgf_search_context(request, query='*', distrib=True, replica=False, latest=True):
    conn = esgf_search_conn(request, distrib)
    ctx = conn.new_context( replica=replica, latest=latest, query=query)
    return ctx

def esgf_aggregation_search(ctx):
    log.debug("datasets found = %d", ctx.hit_count)
    if ctx.hit_count == 0:
        return []
    aggregations = []
    for result in ctx.search():
        agg_ctx = result.aggregation_context()
        log.debug('opendap num files = %d', agg_ctx.hit_count)
        for agg in agg_ctx.search():
            # filter with selected variables
            ok = False
            variables = ctx.facet_constraints.getall('variable')
            log.debug('variables in query: %s', variables)
            if len(variables) > 0:
                for var_name in variables:
                    if var_name in agg.json.get('variable', []):
                        ok = True
                        break
                if not ok: continue

            aggregations.append( (agg.opendap_url, agg.aggregation_id) )
    return aggregations

def esgf_file_search(ctx, start, end):
    from dateutil import parser
    start_date = parser.parse(start)
    end_date = parser.parse(end)
    start_str = '%04d%02d%02d' % (start_date.year, start_date.month, start_date.day)
    end_str = '%04d%02d%02d' % (end_date.year, end_date.month, end_date.day)

    log.debug("filter from=%s, to=%s", start_str, end_str)
    
    log.debug("datasets found = %d", ctx.hit_count)
    files = []
    for result in ctx.search():
        file_ctx = result.file_context()
        log.debug("files found = %d", file_ctx.hit_count)

        query_dict = MultiDict()
        query_dict['type'] = 'File'
        query_dict.extend(file_ctx.facet_constraints)
        query_dict.extend(ctx.facet_constraints)

        log.debug('before sending query ...')
        response = ctx.connection.send_search(limit=file_ctx.hit_count, query_dict=query_dict)
        log.debug('got query response')
        docs = response['response']['docs']
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
            # match overlapping time range
            if f_end >= start_str and f_start <= end_str:
                files.append( (download_url, filename) )
    return files
