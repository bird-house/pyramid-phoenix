import logging
LOGGER = logging.getLogger("PHOENIX")


def includeme(config):
    # settings = config.registry.settings

    LOGGER.debug('Add services')

    config.add_route('services', '/services')
    config.add_route('register_service', '/services/register')
    config.add_route('service_details', '/services/{service_id}')

    config.include('phoenix.services.views.actions')
