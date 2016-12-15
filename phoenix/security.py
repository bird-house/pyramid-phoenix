"""
see pyramid security:

* http://docs.pylonsproject.org/projects/pyramid/en/latest/tutorials/wiki2/authentication.html
"""

from datetime import datetime

from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.exceptions import HTTPForbidden
from pyramid.security import (
    Allow,
    Everyone,
    Authenticated,
    ALL_PERMISSIONS)

from authomatic import Authomatic, provider_id
from authomatic.providers import oauth2, openid
from phoenix.providers import oauth2 as myoauth2
from phoenix.providers import esgfopenid


from twitcher.tokens import tokengenerator_factory
from twitcher.tokens import tokenstore_factory
from twitcher.registry import service_registry_factory

from phoenix.db import mongodb

import logging
logger = logging.getLogger(__name__)

Admin = 'group.admin'
User = 'group.user'
Guest = 'group.guest'


def has_execute_permission(request, service_name):
    service_registry = service_registry_factory(request.registry)
    return service_registry.is_public(service_name) or request.has_permission('submit')


def generate_access_token(registry, userid=None):
    db = mongodb(registry)

    tokengenerator = tokengenerator_factory(registry)
    access_token = tokengenerator.create_access_token(valid_in_hours=8, user_environ={})
    tokenstore = tokenstore_factory(registry)
    tokenstore.save_token(access_token)
    token = access_token['token']
    expires = datetime.utcfromtimestamp(
        int(access_token['expires_at'])).strftime(format="%Y-%m-%d %H:%M:%S UTC")
    if userid:
        db.users.update_one({'identifier': userid},
                            {'$set': {'twitcher_token': token, 'twitcher_token_expires': expires}})


def auth_protocols(request):
    # TODO: refactor auth settings handling
    settings = request.db.settings.find_one()
    protocols = ['phoenix', 'esgf', 'openid', 'ldap', 'oauth2']
    if settings:
        if 'auth' in settings:
            if 'protocol' in settings['auth']:
                protocols = settings['auth']['protocol']
    return protocols


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
    user = request.db.users.find_one({'identifier': userid})
    if user:
        if user.get('group') == Admin:
            return [Admin]
        elif user.get('group') == User:
            return [User]
        else:
            return [Guest]
    return HTTPForbidden()


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
        'esgf_slcs': {
            'class_': myoauth2.ESGF,
            'esgf_slcs_url': request.registry.settings.get('esgf.slcs.url'),
            'consumer_key': request.registry.settings.get('esgf.slcs.cliend.id'),
            'consumer_secret': request.registry.settings.get('esgf.slcs.client.secret'),
            'id': provider_id(),
            'scope': myoauth2.ESGF.user_info_scope,
            'state': 'esgf_slcs',
            'redirect_uri': request.registry.settings.get('esgf.slcs.redirect.uri'),
        },
    }

    # Concatenate the configs.
    config = {}
    config.update(OAUTH2)
    config.update(OPENID)
    config.update(ESGF)
    config['__defaults__'] = DEFAULTS
    return config


class MyAuthenticationPolicy(AuthTktAuthenticationPolicy):
    def authenticated_userid(self, request):
        user = request.user
        if user is not None:
            return user.get('identifier')


def get_user(request):
    user_id = request.unauthenticated_userid
    if user_id is not None:
        user = request.db.users.find_one({'identifier': user_id})
        return user


def includeme(config):
    settings = config.get_settings()

    authn_policy = MyAuthenticationPolicy(
        settings.get('authomatic.secret'),
        callback=groupfinder,
        hashalg='sha512')
    authz_policy = ACLAuthorizationPolicy()
    config.set_root_factory(root_factory)
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)
    config.add_request_method(get_user, 'user', reify=True)
