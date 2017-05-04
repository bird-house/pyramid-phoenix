from pyramid.events import NewRequest

from phoenix.events import SettingsChanged

import logging
LOGGER = logging.getLogger("PHOENIX")


def includeme(config):
    settings = config.registry.settings

    config.add_route('settings', '/settings')
    config.add_route('settings_ldap', '/settings/ldap')
    config.add_route('settings_solr', '/settings/solr/{tab}')
    config.add_route('settings_processes', '/settings/processes')

    def add_solr(event):
        settings = event.request.registry.settings
        if settings.get('_solr', False) is False:
            LOGGER.debug("init solr settings")
            stored_settings = event.request.db.settings.find_one()
            stored_settings = stored_settings or {}
            LOGGER.debug('update solr settings from database')
            settings['solr.maxrecords'] = stored_settings.get('solr_maxrecords', -1)
            settings['solr.depth'] = stored_settings.get('solr_depth', 2)
            settings['_solr'] = True
    config.add_subscriber(add_solr, NewRequest)

    def update_settings(event):
        settings = event.request.registry.settings
        settings.update(event.converted_settings())
    config.add_subscriber(update_settings, SettingsChanged)
