

from pyramid.security import (
	Allow, 
	Everyone, 
	Authenticated, 
	ALL_PERMISSIONS)

# Authentication and Authorization

class Root(object):
    __acl__ = [
                (Allow, Everyone, 'view'),
                (Allow, Authenticated, 'edit'),
               #(Allow, 'group:%s' % ADMIN_GROUP, ALL_PERMISSIONS)
               ]

    def __init__(self, request):
        self.request = request
