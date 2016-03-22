import logging
logger = logging.getLogger(__name__)

def includeme(config):
    settings = config.registry.settings

    logger.info('Adding dashboard ...')

    config.add_route('dashboard', '/dashboard/{tab}')
