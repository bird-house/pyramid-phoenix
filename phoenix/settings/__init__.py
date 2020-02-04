from pyramid.events import NewRequest

from phoenix.events import SettingsChanged

import logging
LOGGER = logging.getLogger("PHOENIX")


def includeme(config):
    # settings = config.registry.settings

    config.add_route('settings', '/settings')
    config.add_route('settings_processes', '/settings/processes')

    def update_settings(event):
        settings = event.request.registry.settings
        settings.update(event.converted_settings())
    config.add_subscriber(update_settings, SettingsChanged)
