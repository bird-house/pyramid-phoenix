from pyramid.events import NewRequest

from phoenix.events import SettingsChanged

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
    config.add_route('settings_processes', '/settings/processes')

    def add_github(event):
        settings = event.request.registry.settings
        if settings.get('_github', False) is False:
            logger.debug("init github settings")
            stored_settings = event.request.db.settings.find_one()
            stored_settings = stored_settings or {}
            if settings.get('github.client.id'):
                logger.debug('update github settings in database')
                stored_settings['github_client_id'] = settings['github.client.id']
                stored_settings['github_client_secret'] = settings['github.client.secret']
                event.request.db.settings.save(stored_settings)
            else:
                logger.debug('update github settings from database')
                settings['github.client.id'] = stored_settings.get('github_client_id')
                settings['github.client.secret'] = stored_settings.get('github_client_secret')
                # TODO: backward compatibility ... please remove!
                if 'github_client_id' not in stored_settings and 'github' in stored_settings:
                    settings['github.client.id'] = stored_settings['github'].get('consumer_key')
                    settings['github.client.secret'] = stored_settings['github'].get('consumer_secret')
            settings['_github'] = True
    config.add_subscriber(add_github, NewRequest)

    def add_esgf(event):
        settings = event.request.registry.settings
        if settings.get('_esgf', False) is False:
            logger.debug("init esgf settings")
            stored_settings = event.request.db.settings.find_one()
            stored_settings = stored_settings or {}
            if settings.get('esgf.slcs.client.id'):
                logger.debug('update esgf settings in database')
                stored_settings['esgf_slcs_url'] = settings.get('esgf.slcs.url')
                stored_settings['esgf_slcs_client_id'] = settings.get('esgf.slcs.client.id')
                stored_settings['esgf_slcs_client_secret'] = settings.get('esgf.slcs.client.secret')
                event.request.db.settings.save(stored_settings)
            else:
                logger.debug('update esgf settings from database')
                settings['esgf.slcs.url'] = stored_settings.get('esgf_slcs_url')
                settings['esgf.slcs.client.id'] = stored_settings.get('esgf_slcs_client_id')
                settings['esgf.slcs.client.secret'] = stored_settings.get('esgf_slcs_client_secret')
            settings['_esgf'] = True
    config.add_subscriber(add_esgf, NewRequest)

    def add_solr(event):
        settings = event.request.registry.settings
        if settings.get('_solr', False) is False:
            logger.debug("init solr settings")
            stored_settings = event.request.db.settings.find_one()
            stored_settings = stored_settings or {}
            logger.debug('update solr settings from database')
            settings['solr.maxrecords'] = stored_settings.get('solr_maxrecords', -1)
            settings['solr.depth'] = stored_settings.get('solr_depth', 2)
            settings['_solr'] = True
    config.add_subscriber(add_solr, NewRequest)

    def update_settings(event):
        settings = event.request.registry.settings
        settings.update(event.converted_settings())
    config.add_subscriber(update_settings, SettingsChanged)
