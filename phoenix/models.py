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

from phoenix import helpers
from .helpers import mongodb_conn, esgsearch_url
from .wps import get_wps, wps_url, gen_token

import logging
logger = logging.getLogger(__name__)

# mongodb ...
# -----------

def database(request):
    conn = mongodb_conn(request)
    return conn.phoenix_db

# registered users (whitelist)

def register_user(request,
                  user_id,
                  openid=None,
                  name=None,
                  organisation=None,
                  notes=None,
                  activated=False):
    db = database(request)
    user = db.users.find_one(dict(user_id = user_id))
    if user != None:
        unregister_user(request, user_id = user_id)
    user = dict(
        user_id = user_id,
        openid = openid,
        name = name,
        organisation = organisation,
        notes = notes,
        activated = activated,
        creation_time = datetime.datetime.now(),
        last_login = datetime.datetime.now(),
        )
    db.users.save(user)
    return user

def unregister_user(request, user_id):
    db = database(request)
    db.users.remove(dict(user_id = user_id))

def activate_user(request, user_id):
    update_user(request, user_id, activated=True)

def deactivate_user(request, user_id):
    update_user(request, user_id, activated=False)

def update_user(request,
                user_id,
                openid=None,
                name=None,
                organisation=None,
                notes=None,
                activated=None,
                credentials=None,
                update_token=True,
                update_login=True):
    logger.debug("update user %s", user_id)
       
    db = database(request)
    user = db.users.find_one(dict(user_id = user_id))
    if user == None:
        user = register_user(request, user_id=user_id, activated=False)
    if activated is not None:
        user['activated'] = activated
    if openid is not None:
        user['openid'] = openid
    if name is not None:
        user['name'] = name
    if organisation is not None:
        user['organisation'] = organisation
    if notes is not None:
        user['notes'] = notes
    if credentials is not None:
        user['credentials'] = credentials
    if update_token:
         try:
             wps = get_wps(wps_url(request))
             user['token'] = gen_token(wps, helpers.sys_token(request), user_id)
         except Exeption as e:
             logger.error('Could not generate token for user %s, err msg=%s' % (user_id, e.message))
    if update_login:
        user['last_login'] = datetime.datetime.now()
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

def is_user_activated(request, user_id):
    db = database(request)
    return None != db.users.find_one(dict(user_id = user_id, activated = True))

def count_users(request):
    db = database(request)
    return db.users.count()

def user_with_id(request, user_id):
    db = database(request)
    return db.users.find_one(dict(user_id = user_id))

def user_openid(request, user_id):
    db = database(request)
    user = db.users.find_one(dict(user_id = user_id))
    return user.get('openid')

def user_token(request, user_id):
    db = database(request)
    user = db.users.find_one(dict(user_id = user_id))
    return user.get('token')

def user_credentials(request, user_id):
    db = database(request)
    user = db.users.find_one(dict(user_id = user_id))
    return user.get('credentials')

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
    #logger.debug('count jobs = %s', db.jobs.count())

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
    from owslib.wps import WPSExecution

    dateformat = '%a, %d %b %Y %I:%M:%S %p'
    jobs = []
    for job in jobs_by_userid(request, user_id=authenticated_userid(request)):

        job['starttime'] = job['start_time'].strftime(dateformat)

        # TODO: handle different process status
        if job['status'] in ['ProcessAccepted', 'ProcessStarted', 'ProcessPaused']:
            job['errors'] = []
            try:
                wps = get_wps(job['service_url'])
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
                logger.warn(msg)
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

