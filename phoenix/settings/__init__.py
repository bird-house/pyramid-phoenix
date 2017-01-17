from pyramid.events import NewRequest

import logging
logger = logging.getLogger(__name__)


def includeme(config):
    settings = config.registry.settings

    logger.debug('Enable settings ...')

    config.add_route('settings', '/settings')
    config.add_route('settings_auth', '/settings/auth')
    config.add_route('settings_ldap', '/settings/ldap')
    config.add_route('settings_github', '/settings/github')
    config.add_route('settings_esgf', '/settings/esgf')
    config.add_route('settings_solr', '/settings/solr/{tab}')

    def add_github(event):
        settings = event.request.registry.settings
        stored_settings = event.request.db.settings.find_one()
        stored_settings = stored_settings or {}
        if settings.get('github.client.id'):
            stored_settings['github_client_id'] = settings.get('github.client.id')
            stored_settings['github_client_secret'] = settings.get('github.client.secret')
            event.request.db.settings.save(stored_settings)
        else:
            settings['github.client.id'] = stored_settings.get('github_client_id')
            settings['github.client.secret'] = stored_settings.get('github_client_secret')
    config.add_subscriber(add_github, NewRequest)

    def add_esgf(event):
        settings = event.request.registry.settings
        stored_settings = event.request.db.settings.find_one()
        stored_settings = stored_settings or {}
        if settings.get('esgf.slcs.client.id'):
            stored_settings['esgf_slcs_url'] = settings.get('esgf.slcs.url')
            stored_settings['esgf_slcs_client_id'] = settings.get('esgf.slcs.client.id')
            stored_settings['esgf_slcs_client_secret'] = settings.get('esgf.slcs.client.secret')
            event.request.db.settings.save(stored_settings)
        else:
            settings['esgf.slcs.url'] = stored_settings.get('esgf_slcs_url')
            settings['esgf.slcs.client.id'] = stored_settings.get('esgf_slcs_client_id')
            settings['esgf.slcs.client.secret'] = stored_settings.get('esgf_slcs_client_secret')
    config.add_subscriber(add_esgf, NewRequest)

    def add_solr(event):
        settings = event.request.registry.settings
        stored_settings = event.request.db.settings.find_one()
        stored_settings = stored_settings or {}
        settings['solr.maxrecords'] = stored_settings.get('solr_maxrecords', -1)
        settings['solr.depth'] = stored_settings.get('solr_depth', 2)
    config.add_subscriber(add_solr, NewRequest)
