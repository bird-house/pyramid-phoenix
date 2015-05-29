import logging
logger = logging.getLogger(__name__)

def admin_users(request):
    value = request.registry.settings.get('phoenix.admin_users')
    if value is not None:
        import re
        return map(str.strip, re.split("\\s+", value.strip()))
    return []

def groupfinder(userid, request):
    """Dispatch groupfinders for different authentication methods."""
    if userid.lower().startswith('cn='):
        # 'userid' is a ldap dn
        return groupfinder_ldap(userid, request)
    else:
        # Assumption: 'userid' is an email address
        return groupfinder_email(userid, request)

def groupfinder_ldap(userdn, request):
    from pyramid_ldap import get_ldap_connector
    connector = get_ldap_connector(request)
    group_list = connector.user_groups(userdn)
    logger.debug('ldap groups for %s: %s', userdn, group_list)

    if group_list is None:
        return None
    # TODO: Translate ldap groups in some way...
    return ['group:admins']

def groupfinder_email(email, request):
    admins = admin_users(request)
    
    if email in admins:
        return ['group:admins']
    # FK: Is this fix okay, or was the previous line intended to fail the way it did?
    elif request.db.users.find_one({'email':email}) is not None \
            and request.db.users.find_one({'email':email}).get('activated'):
        return ['group:editors']
    else:
        # FK: Is this equivalent to return None?
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
                # FK: Authenticated should be sufficient to see the 'logout' page. Maybe a TODO.
                #(Allow, Authenticated, 'edit'),
                (Allow, 'group:editors', 'edit'),
                (Allow, 'group:admins', ALL_PERMISSIONS)
               ]

    def __init__(self, request):
        self.request = request

def root_factory(request):
    return Root(request)

