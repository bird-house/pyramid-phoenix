# models.py
# Copyright (C) 2013 the ClimDaPs/Phoenix authors and contributors
# <see AUTHORS file>
#
# This module is part of ClimDaPs/Phoenix and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

# TODO: refactor usage of mongodb etc ...

import pymongo

from pyramid.security import authenticated_userid

from pyramid.security import (
    Allow,
    Everyone,
    )

import uuid
import datetime

from owslib.wps import WebProcessingService

from .wps import gen_token
from .exceptions import TokenError

import logging
logger = logging.getLogger(__name__)

class Catalog():
    """ This class provides access to the catalogs in mongodb."""
    
    def __init__(self, request):
        self.request = request
        self.db = request.db

    def add(self, url, notes=None):
        entry = None
        try:
            wps = WebProcessingService(url=url.split('?')[0])

            entry = self.db.catalog.find_one(dict(url = wps.url))
            if entry is not None:
                self.db.catalog.remove(dict(url = wps.url))
            entry = dict(
                format = 'WPS',
                url = wps.url,
                title = wps.identification.title,
                abstract = wps.identification.abstract,
                notes = notes,
                )
            self.db.catalog.save(entry)

            msg='Added wps %s succesfully' % (wps.url)
            logger.info(msg)
            self.request.session.flash(msg, queue='info')
        except:
            msg='Could not add wps %s' % (wps.url)
            logger.exception(msg)
            self.request.session.flash(msg, queue='error')

        return entry

    def delete(self, url):
        try:
            self.db.catalog.remove(dict(url=url))
            msg='Removed wps %s succesfully' % (url)
            logger.info(msg)
            self.request.session.flash(msg, queue='info')
        except:
            logger.exception('could not delete wps %s in catalog', url)

    def by_url(self, url):
        entry = None
        try:
            entry = self.db.catalog.find_one(dict(url = url))
        except:
            logger.exception('could not find wps %s in catalog', url)
        return entry

    def all(self):
        return self.db.catalog.find(dict(format='WPS'))

    def all_as_tuple(self):
        return map(lambda entry: (entry['url'], '%s (%s)' % (entry.get('title', 'unknown'), entry.get('notes', ''))), self.all())


class User():
    """ This class provides access to the users in mongodb."""
    
    def __init__(self, request):
        self.request = request
        self.db = request.db

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
                if self.request.wps is None:
                    msg = 'Malleefowl WPS is not available.'
                    self.request.session.flash(msg, queue='error')
                    raise Exception(msg)
                user['token'] = gen_token(
                    self.request.wps,
                    self.request.registry.settings.get('malleefowl.sys_token'),
                    user_id)
                msg = "Your access token was successfully updated. See <a href='/account'>My Account</a>"
                logger.info(msg)
                self.request.session.flash(msg, queue='info')
            except:
                msg = 'Could not generate token for user %s' % (user_id)
                logger.exception(msg)
                self.request.session.flash(msg, queue='error')
                raise TokenError(msg)
        if update_login:
            user['last_login'] = datetime.datetime.now()
        self.db.users.update(dict(user_id = user_id), user)

    def all(self, key='activated', direction=pymongo.ASCENDING):
        return self.db.users.find().sort(key, direction)

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

def add_job(request,
            identifier,
            wps_url,
            execution,
            user_id='anonymous',
            notes='',
            tags=''):
    request.db.jobs.save(dict(
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



    
