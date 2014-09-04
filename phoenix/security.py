import logging
logger = logging.getLogger(__name__)

def admin_users(request):
    value = request.registry.settings.get('phoenix.admin_users')
    if value is not None:
        import re
        return map(str.strip, re.split("\\s+", value.strip()))
    return []

def groupfinder(email, request):
    admins = admin_users(request)
    
    if email in admins:
        return ['group:admins']
    elif request.db.users.find_one({'email':email}).get('activated'):
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

