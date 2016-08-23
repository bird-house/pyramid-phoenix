import logging
logger = logging.getLogger(__name__)

def includeme(config):
    settings = config.registry.settings

    logger.info('Add processes')

    config.add_route('processes', '/processes')
    config.add_route('processes_list', '/processes/list')
    config.add_route('processes_execute', '/processes/execute')
    config.add_route('processes_loading', '/processes/loading')
    config.add_route('processes_check_queue', '/processes/check_queue.json')
