from .helpers import admin_users
import models

import logging
logger = logging.getLogger(__name__)

def is_valid_user(request, user_id):
    if user_id in admin_users(request):
        return True
    userdb = models.User(request)
    return userdb.is_activated(user_id)

def groupfinder(user_id, request):
    admins = admin_users(request)
    userdb = models.User(request)
    
    if user_id in admins:
        return ['group:admins']
    elif userdb.is_activated(user_id):
        return ['group:editors']
    else:
        return ['group:views']


from pyramid.security import (
        Allow, 
        Everyone, 
        Authenticated, 
        ALL_PERMISSIONS)

# Authentication and Authorization

class Root():
    __acl__ = [
                (Allow, Everyone, 'view'),
                #(Allow, Authenticated, 'edit'),
                (Allow, 'group:editors', 'edit'),
                (Allow, 'group:admins', ALL_PERMISSIONS)
               ]

    def __init__(self, request):
        self.request = request

def root_factory(request):
    return Root(request)

