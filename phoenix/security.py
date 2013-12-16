from .helpers import admin_users
from .models import is_user_activated

import logging

log = logging.getLogger(__name__)

def is_valid_user(request, user_id):
    if user_id in admin_users(request):
        return True
    return is_user_activated(request, user_id)

def groupfinder(user_id, request):
    #log.debug('groupfinder: user_id=%s', user_id)
    admins = admin_users(request)
    
    if user_id in admins:
        return ['group:admins']
    elif is_user_activated(request, user_id):
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

