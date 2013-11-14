ADMIN_USERS = ['ehbrecht@dkrz.de', 'carsten@linacs.org', 'nils.hempelmann@hzg.de', 'kipp@dkrz.de']

def groupfinder(userid, request):
    log.debug('groupfinder: userid=%s', userid)
    
    if userid in ADMIN_USERS:
        return ['group:admins']
    else:
        return ['group:editors']


from pyramid.security import (
	Allow, 
	Everyone, 
	Authenticated, 
	ALL_PERMISSIONS)
from persistent.mapping import PersistentMapping

# Authentication and Authorization

def root_factory(request):
    log.debug('called root_factory')
    return Phoenix(request)

class Phoenix(PersistentMapping):
    __name__ = None
    __parent__ = None
    __acl__ = [
                (Allow, Everyone, 'view'),
                (Allow, Authenticated, 'edit'),
                (Allow, 'group:admins', ALL_PERMISSIONS)
               ]

    def __init__(self, request):
        self.request = request

