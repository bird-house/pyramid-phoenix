import logging
LOGGER = logging.getLogger("PHOENIX")


def includeme(config):
    # settings = config.registry.settings

    LOGGER.debug('Add supervisor')

    config.add_route('supervisor', '/supervisor')
    config.add_route('supervisor_process', '/supervisor/{action}/{name}')
    config.add_route('supervisor_log', '/supervisor_log/{name}')
