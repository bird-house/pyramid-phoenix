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
from .helpers import mongodb_conn
from .wps import get_wps, wps_url, gen_token
from .exceptions import TokenError

import logging
logger = logging.getLogger(__name__)

# mongodb ...
# -----------

def database(request):
    conn = mongodb_conn(request)
    return conn.phoenix_db


class User():
    """ This class provides access to the users in mongodb."""
    
    def __init__(self, request):
        self.request = request
        self.db = database(request)

    def add(self,
            user_id,
            openid=None,
            name=None,
            organisation=None,
            notes=None,
            activated=False):
        user = self.db.users.find_one(dict(user_id = user_id))
        if user != None:
            delete(user_id = user_id)
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
        self.db.users.save(user)
        return user

    def delete(self, user_id):
        self.db.users.remove(dict(user_id = user_id))

    def activate(self, user_id):
        self.update(user_id, activated = not self.is_activated(user_id))

    def update(self,
                user_id,
                openid=None,
                name=None,
                organisation=None,
                notes=None,
                activated=None,
                credentials=None,
                cert_expires=None,
                update_token=False,
                update_login=True):
        logger.debug("update user %s", user_id)

        user = self.db.users.find_one(dict(user_id = user_id))
        if user == None:
            user = self.add(user_id=user_id, activated=False)
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
        if cert_expires is not None:
            user['cert_expires'] = cert_expires
        if update_token:
             try:
                 wps = get_wps(wps_url(self.request))
                 user['token'] = gen_token(wps, helpers.sys_token(self.request), user_id)
                 msg = "Your access token was successfully updated. See <a href='/account'>My Account</a>"
                 logger.info(msg)
                 self.request.session.flash(msg, queue='info')
             except Exception as e:
                 msg = 'Could not generate token for user %s, err msg=%s' % (user_id, e.message)
                 logger.error(msg)
                 self.request.session.flash(msg, queue='error')
                 raise TokenError(msg)
        if update_login:
            user['last_login'] = datetime.datetime.now()
        self.db.users.update(dict(user_id = user_id), user)

    def all(self):
        return self.db.users.find()

    def is_activated(self, user_id):
        return None != self.db.users.find_one(dict(user_id = user_id, activated = True))

    def count(self):
        d = datetime.datetime.now() - datetime.timedelta(hours=3)
        num_logins_3h = self.db.users.find({"last_login": {"$gt": d}}).count()

        d = datetime.datetime.now() - datetime.timedelta(days=7)
        num_logins_7d = self.db.users.find({"last_login": {"$gt": d}}).count()

        return dict(num_users=self.db.users.count(),
                    num_logins_3h=num_logins_3h,
                    num_logins_7d=num_logins_7d)

    def by_id(self, user_id):
        return self.db.users.find_one(dict(user_id = user_id))

    def openid(self, user_id):
        user = self.db.users.find_one(dict(user_id = user_id))
        return user.get('openid')

    def token(self, user_id):
        user = self.db.users.find_one(dict(user_id = user_id))
        return user.get('token')

    def is_token_valid(self, user_id):
        token = self.token(user_id)
        if token is None or len(token) < 22:
            return False
        return True

    def credentials(self, user_id):
        user = self.db.users.find_one(dict(user_id = user_id))
        return user.get('credentials')

class Job():
    """This class provides access to the jobs in mongodb."""
    def __init__(self, request):
        self.request = request
        self.db = database(request)


    def add(self,
            identifier,
            wps_url,
            execution,
            user_id='anonymous',
            notes='',
            tags=''):
        self.db.jobs.save(dict(
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

    def by_id(self, uuid):
        job = self.db.jobs.find_one({'uuid': uuid})
        return job

    def update(self, job):
        self.db.jobs.update({'uuid': job['uuid']}, job)

    def count(self):
        return self.db.jobs.count()

    def drop(self):
        self.db.jobs.drop()

    def by_userid(self, user_id='anonymous'):
        return self.db.jobs.find( dict(user_id=user_id) )

    def drop_by_user_id(self, user_id):
        for job in self.by_userid(user_id):
            self.db.jobs.remove({"uuid": job['uuid']})

    def drop_by_ids(self, uuids=[]):
        for uuid in uuids:
            self.db.jobs.remove({"uuid": uuid})

    def information(self, sortkey="starttime", inverted=True):
        """
        Collects jobs status ...

        TODO: rewrite code
        """
        from owslib.wps import WPSExecution

        dateformat = '%a, %d %b %Y %I:%M:%S %p'
        jobs = []
        for job in self.by_userid(user_id=authenticated_userid(self.request)):

            job['starttime'] = job['start_time'].strftime(dateformat)

            # TODO: handle different process status
            # TODO: check Exception ... wps needs some time to provide status document which may cause an exception
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
                    msg = 'could not access wps %s' % ( job['status_location'] )
                    logger.exception(msg)
                    # TODO: if url is not accessable ... try again!
                    job['status'] = 'ProcessFailed'
                    job['errors'].append( dict(code='', locator='', text=msg) )

                job['end_time'] = datetime.datetime.now()
                for err in job['errors']:
                    job['error_message'] = err.get('text', '') + ';'

                # TODO: configure output delete time
                dd = 3
                job['output_delete_time'] = datetime.datetime.now() + datetime.timedelta(days=dd)
                job['duration'] = str(job['end_time'] - job['start_time'])
                self.update(job)
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

