import logging
logger = logging.getLogger(__name__)

def includeme(config):
    settings = config.registry.settings

    logger.info('Adding solr ...')

    # actions
    config.add_route('index_service', '/solr/{service_id}/index')
    config.add_route('clear_index', '/solr/clear')
    
