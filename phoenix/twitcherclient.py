from urlparse import urlparse

from twitcher.client import TwitcherService

from phoenix.db import mongodb


def includeme(config):
    settings = config.registry.settings

    config.include('twitcher.rpcinterface')
    config.include('twitcher.owsproxy')
    config.include('twitcher.tweens')


def twitcher_service_factory(registry):
    settings = registry.settings
    service = TwitcherService(url=settings.get('twitcher.url'), verify=False)
    return service


def generate_access_token(registry, userid=None, valid_in_hours=1):
    settings = registry.settings
    service = twitcher_service_factory(registry)
    db = mongodb(registry)
    collection = db.users

    environ = {}
    user = collection.find_one({'identifier': userid})
    esgf_token = user.get('esgf_token')
    if esgf_token:
        environ['esgf_access_token'] = esgf_token.get('access_token')
        environ['esgf_slcs_service_url'] = settings.get('esgf.slcs.url')

    # call to service
    token = service.generate_token(valid_in_hours, environ)
    if userid and token:
        collection.update_one(
            {'identifier': userid},
            {'$set': {'twitcher_token': token, }})
    return token


def is_public(registry, name):
    srv = twitcher_service_factory(registry)
    service = srv.get_service_by_name(name)
    return service.get('public', False)
