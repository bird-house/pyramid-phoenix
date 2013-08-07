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
    
def esgf_search_context(request):
    conn = esgf_search_conn(request)
    ctx = conn.new_context(
        project='CMIP5', product='output1', 
        replica=False, latest=True)
    return ctx
