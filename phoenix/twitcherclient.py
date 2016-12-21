import xmlrpclib
import ssl
from urlparse import urlparse
from datetime import datetime

from phoenix.db import mongodb


def includeme(config):
    settings = config.registry.settings

    config.include('twitcher.rpcinterface')
    config.include('twitcher.owsproxy')
    config.include('twitcher.tweens')


def _create_https_context(verify=True):
    context = ssl._create_default_https_context()
    if verify is False:
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
    return context


def _create_server(url, verify=True, username=None, password=None):
    # TODO: disable basicauth when username is not set
    username = username or 'nouser'
    password = password or 'nopass'

    parsed = urlparse(url)
    url = "%s://%s:%s@%s%s" % (parsed.scheme, username, password, parsed.netloc, parsed.path)
    context = _create_https_context(verify=verify)
    server = xmlrpclib.ServerProxy(url, context=context)
    return server


def generate_access_token(registry, userid=None, valid_in_hours=1):
    client = TwitcherClient(registry)
    return client.get_token(userid=userid, valid_in_hours=valid_in_hours)


def is_public(registry, name):
    client = TwitcherClient(registry)
    return client.is_public(name)


class TwitcherClient(object):
    def __init__(self, registry):
        self.registry = registry
        self.settings = registry.settings
        db = mongodb(registry)
        self.collection = db.users
        self.server = _create_server("https://localhost:8443", verify=False)

    def get_token(self, userid=None, valid_in_hours=1):
        environ = {}
        user = self.collection.find_one({'identifier': userid})
        esgf_token = user.get('esgf_token')
        if esgf_token:
            environ['esgf_access_token'] = esgf_token.get('access_token')
            environ['esgf_slcs_service_url'] = self.settings.get('esgf.slcs.url')

        token = self.server.gentoken(valid_in_hours, environ)
        expires = datetime.utcfromtimestamp(
            int(token['expires_at'])).strftime(format="%Y-%m-%d %H:%M:%S UTC")
        if userid:
            self.collection.update_one(
                {'identifier': userid},
                {'$set': {'twitcher_token': token['access_token'], 'twitcher_token_expires': expires}})

    def register_service(self, url, name=None, service_type=None, public=False, c4i=False, overwrite=True):
        service_type = service_type or 'wps'
        self.server.register(url, name, service_type, public, c4i, overwrite)

    def unregister_service(self, name):
        self.server.register(name)

    def clear_services(self):
        self.server.purge()

    def is_public(self, name):
        return self.server.is_public(name)

    def get_service_name(self, url):
        return self.server.get_service_name(url)

    def get_service_by_url(self, url):
        return self.server.get_service_by_url(url)

    def get_service_by_name(self, name):
        return self.server.get_service_by_name(name)
