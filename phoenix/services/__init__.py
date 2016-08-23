import logging
logger = logging.getLogger(__name__)

def includeme(config):
    settings = config.registry.settings

    logger.info('Add services')

    config.add_route('services', '/services')
    config.add_route('register_service', '/services/register')
    config.add_route('service_details', '/services/{service_id}')

    config.include('phoenix.services.views.actions')
    
