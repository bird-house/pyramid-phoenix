from pyramid.events import NewRequest

import logging
logger = logging.getLogger(__name__)


def load_settings(request):
    defaults = dict(solr_maxrecords=-1, solr_depth=2)

    collection = request.db.settings
    settings = collection.find_one()
    if not settings:
        collection.save(defaults)
        settings = collection.find_one()
    for key in defaults.keys():
        if not key in settings:
            settings[key] = defaults[key]
    return settings


def includeme(config):
    settings = config.registry.settings

    logger.info('Add Settings')

    config.add_route('settings', '/settings')
    config.add_route('settings_auth', '/settings/auth')
    config.add_route('settings_ldap', '/settings/ldap')
    config.add_route('settings_github', '/settings/github')
    config.add_route('settings_esgf', '/settings/esgf')
    config.add_route('settings_solr', '/settings/solr/{tab}')

    def add_github(event):
        settings = event.request.registry.settings
        if not settings.get('github.consumer.key'):
            _settings = event.request.db.settings.find_one()
            _settings = _settings or {}
            settings['github.consumer.key'] = _settings.get('github_consumer_key')
            settings['github.consumer.secret'] = _settings.get('github_consumer_secret')
    config.add_subscriber(add_github, NewRequest)

    def add_esgf(event):
        settings = event.request.registry.settings
        if not settings.get('esgf.slcs.client.id'):
            _settings = event.request.db.settings.find_one()
            _settings = _settings or {}
            settings['esgf.slcs.url'] = _settings.get('esgf_slcs_url')
            settings['esgf.slcs.client.id'] = _settings.get('esgf_slcs_client_id')
            settings['esgf.slcs.client.secret'] = _settings.get('esgf_slcs_client_secret')
    config.add_subscriber(add_github, NewRequest)
