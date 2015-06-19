import logging
logger = logging.getLogger(__name__)

Admin = 'group.admin'
User = 'group.user'
Guest = 'group.guest'

# TODO: make this configurable
ESGF_Provider = dict(
    BADC='https://ceda.ac.uk/openid/%s',
    BNU='https://esg.bnu.edu.cn/esgf-idp/openid/%s',
    DKRZ='https://esgf-data.dkrz.de/esgf-idp/openid/%s',
    IPSL='https://esgf-node.ipsl.fr/esgf-idp/openid/%s',
    NCI='https://esg2.nci.org.au/esgf-idp/openid/%s',
    PCMDI='https://pcmdi9.llnl.gov/esgf-idp/openid/%s',
    SMHI='https://esg-dn1.nsc.liu.se/esgf-idp/openid/%s',
    )

def admin_users(request):
    admins = set()
    for admin in request.db.users.find({'group':Admin}):
        admins.add(admin.get('email'))
    value = request.registry.settings.get('phoenix.admin_users')
    if value is not None:
        import re
        for email in map(str.strip, re.split("\\s+", value.strip())):
            admins.add(email)
    return admins

def groupfinder(email, request):
    admins = admin_users(request)
    user = request.db.users.find_one({'email':email})

    if email in admins or user.get('group') == Admin:
        return [Admin]
    elif user.get('group') == User:
        return [User]
    else:
        return [Guest]

from pyramid.security import (
        Allow, 
        Everyone, 
        Authenticated, 
        ALL_PERMISSIONS)

# Authentication and Authorization

class Root():
    __acl__ = [
                (Allow, Everyone, 'view'),
                (Allow, Authenticated, 'edit'),
                (Allow, User, 'submit'),
                (Allow, Admin, ALL_PERMISSIONS)
               ]

    def __init__(self, request):
        self.request = request

def root_factory(request):
    return Root(request)

# Authomatic

from authomatic.providers import oauth2, openid
from authomatic import Authomatic, provider_id

def authomatic(request):
    return Authomatic(
        config=authomatic_config(request),
        secret=request.registry.settings.get('authomatic.secret'),
        report_errors=True,
        logging_level=logger.level)

def authomatic_config(request):

    DEFAULTS = {
        'popup': True,
    }

    AUTHENTICATION = {
        'openid': {
            'class_': openid.OpenID,
        },
    }
    
    OAUTH2 = {
        'github': {
            'class_': oauth2.GitHub,
            'consumer_key': request.registry.settings.get('github.consumer.key'),
            'consumer_secret': request.registry.settings.get('github.consumer.secret'),
            'access_headers': {'User-Agent': 'Phoenix'},
            'id': provider_id(),
            'scope': oauth2.GitHub.user_info_scope,
            '_apis': {
                'Get your events': ('GET', 'https://api.github.com/users/{user.username}/events'),
                'Get your watched repos': ('GET', 'https://api.github.com/user/subscriptions'),
            },
        },
    }


    # Concatenate the configs.
    config = {}
    config.update(OAUTH2)
    config.update(AUTHENTICATION)
    config['__defaults__'] = DEFAULTS
    return config

