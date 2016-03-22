import logging
logger = logging.getLogger(__name__)

def includeme(config):
    settings = config.registry.settings

    logger.info('Add supervisor')

    config.add_route('supervisor', '/supervisor')
    config.add_route('supervisor_process', '/supervisor/{action}/{name}')
    config.add_route('supervisor_log', '/supervisor_log/{name}')
