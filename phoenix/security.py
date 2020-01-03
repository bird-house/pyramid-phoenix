"""
see pyramid security:

* http://docs.pylonsproject.org/projects/pyramid/en/latest/tutorials/wiki2/authentication.html
"""

from collections import OrderedDict

from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.security import (
    Allow,
    Everyone,
    Authenticated,
    ALL_PERMISSIONS)
from pyramid.security import unauthenticated_userid
from pyramid.settings import asbool
from pyramid.csrf import check_csrf_token as _check_csrf_token

from authomatic import Authomatic, provider_id
from authomatic.providers import oauth2
from phoenix.providers.oauth2 import CEDAProvider, create_keycloak_provider


import logging
LOGGER = logging.getLogger("PHOENIX")

Admin = 'group.admin'
User = 'group.user'
Guest = 'group.guest'

AUTH_PROTOCOLS = OrderedDict([
    ('phoenix', 'Phoenix'),
    ('github', 'GitHub'),
])


def check_csrf_token(request):
    if request.require_csrf:
        return _check_csrf_token(request)
    return True


def passwd_check(request, passphrase):
    """
    TODO: See passwd_check in IPython.lib.security
    """
    phoenix_passphrase = request.registry.settings.get('phoenix.password', '')
    return phoenix_passphrase == passphrase


def groupfinder(userid, request):
    user = request.db.users.find_one({'identifier': userid})
    if user:
        if user.get('group') == Admin:
            return [Admin]
        elif user.get('group') == User:
            return [User]
    return [Guest]


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
        logging_level=LOGGER.level)


def authomatic_config(request):

    DEFAULTS = {
        'popup': True,
    }

    OAUTH2 = {
        'github': {
            'class_': oauth2.GitHub,
            'consumer_key': request.registry.settings.get('github.client.id'),
            'consumer_secret': request.registry.settings.get('github.client.secret'),
            'access_headers': {'User-Agent': 'Phoenix'},
            'id': provider_id(),
            'scope': oauth2.GitHub.user_info_scope,
            '_apis': {
                'Get your events': ('GET', 'https://api.github.com/users/{user.username}/events'),
                'Get your watched repos': ('GET', 'https://api.github.com/user/subscriptions'),
            },
        },
        'ceda_oauth': {  # Not named 'ceda' to avoid conflict with CEDA OpenID
            'class_': CEDAProvider,
            'consumer_key': request.registry.settings.get('ceda.client.id'),
            'consumer_secret': request.registry.settings.get('ceda.client.secret'),
            'access_headers': {'User-Agent': 'Phoenix'},
            'scope': CEDAProvider.user_info_scope,
        },
        'keycloak': {  # keycloak
            'class_': create_keycloak_provider(
                url=request.registry.settings.get('keycloak.url'),
                realm=request.registry.settings.get('keycloak.realm')),
            'consumer_key': request.registry.settings.get('keycloak.client.id'),
            'consumer_secret': request.registry.settings.get('keycloak.client.secret'),
            'access_headers': {'User-Agent': 'Phoenix'},
            'scope': 'openid email profile',
        },
    }

    # Concatenate the configs.
    config = {}
    config.update(OAUTH2)
    config['__defaults__'] = DEFAULTS
    return config


class MyAuthenticationPolicy(AuthTktAuthenticationPolicy):
    def authenticated_userid(self, request):
        user = request.user
        if user is not None:
            return user.get('identifier')


def get_user(request):
    user_id = unauthenticated_userid(request)
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

    # is csrf checking activated?
    def require_csrf(request):
        settings = request.registry.settings
        return asbool(settings.get('phoenix.require_csrf', 'true'))
    config.add_request_method(require_csrf, reify=True)
    # TODO: configure csrf checks
    # config.set_default_csrf_options(require_csrf=True)
