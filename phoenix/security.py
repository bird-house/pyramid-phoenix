from datetime import datetime

from pyramid.exceptions import HTTPForbidden
from pyramid.security import authenticated_userid

from twitcher.tokens import tokengenerator_factory
from twitcher.tokens import tokenstore_factory

import logging
logger = logging.getLogger(__name__)

Admin = 'group.admin'
User = 'group.user'
Guest = 'group.guest'

def generate_access_token(request, userid):
    user = request.db.users.find_one({'identifier':userid})

    tokengenerator = tokengenerator_factory(request.registry)
    access_token = tokengenerator.create_access_token(valid_in_hours=8, user_environ={})
    tokenstore = tokenstore_factory(request.registry)
    tokenstore.save_token(access_token)
        
    user['twitcher_token'] = access_token['token']
    user['twitcher_token_expires'] = datetime.utcfromtimestamp(
            int(access_token['expires_at'])).strftime(format="%Y-%m-%d %H:%M:%S UTC")
    request.db.users.update({'identifier':userid}, user)

def passwd_check(request, passphrase):
    """
    code taken from IPython.lib.security
    TODO: maybe import ipython
    
    >>> passwd_check('sha1:0e112c3ddfce:a68df677475c2b47b6e86d0467eec97ac5f4b85a',
    ...              'anotherpassword')
    False
    """
    import hashlib
    hashed_passphrase = request.registry.settings.get('phoenix.password', u'')
    
    try:
        algorithm, salt, pw_digest = hashed_passphrase.split(':', 2)
    except (ValueError, TypeError):
        return False

    try:
        h = hashlib.new(algorithm)
    except ValueError:
        return False

    if len(pw_digest) == 0:
        return False

    try:
        h.update(passphrase.encode('utf-8') + salt.encode('ascii'))
    except:
        return False

    return h.hexdigest() == pw_digest


def groupfinder(userid, request):
    user = request.db.users.find_one({'identifier':userid})
    if user:
        if user.get('group') == Admin:
            return [Admin]
        elif user.get('group') == User:
            return [User]
        else:
            return [Guest]
    return HTTPForbidden()


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
from phoenix.providers import oauth2 as myoauth2
from phoenix.providers import esgfopenid
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

    OPENID = {
        'openid': {
            'class_': openid.OpenID,
        },
    }

    ESGF = {
        'dkrz': {
            'class_': esgfopenid.ESGFOpenID,
            'hostname': 'esgf-data.dkrz.de',
        },
        'ipsl': {
            'class_': esgfopenid.ESGFOpenID,
            'hostname': 'esgf-node.ipsl.fr',
        },
        'badc': {
            'class_': esgfopenid.ESGFOpenID,
            'hostname': 'ceda.ac.uk',
            'provider_url': 'https://{hostname}/openid/{username}'
        },
        'pcmdi': {
            'class_': esgfopenid.ESGFOpenID,
            'hostname': 'pcmdi.llnl.gov',
        },
        'smhi': {
            'class_': esgfopenid.ESGFOpenID,
            'hostname': 'esg-dn1.nsc.liu.se',
        },
    }
    
    OAUTH2 = {
        'github': {
            'class_': oauth2.GitHub,
            'consumer_key': request.github_oauth[0],
            'consumer_secret': request.github_oauth[1],
            'access_headers': {'User-Agent': 'Phoenix'},
            'id': provider_id(),
            'scope': oauth2.GitHub.user_info_scope,
            '_apis': {
                'Get your events': ('GET', 'https://api.github.com/users/{user.username}/events'),
                'Get your watched repos': ('GET', 'https://api.github.com/user/subscriptions'),
            },
        },
        'ceda': {
            'class_': myoauth2.Ceda,
            'consumer_key': request.registry.settings.get('ceda.consumer.key'),
            'consumer_secret': request.registry.settings.get('ceda.consumer.secret'),
            'id': provider_id(),
            'scope': myoauth2.Ceda.user_info_scope,
            #'state': 'ceda', 
            'redirect_uri': request.registry.settings.get('ceda.consumer.redirect.uri'),
        },
    }


    # Concatenate the configs.
    config = {}
    config.update(OAUTH2)
    config.update(OPENID)
    config.update(ESGF)
    config['__defaults__'] = DEFAULTS
    return config


