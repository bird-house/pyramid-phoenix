import logging
logger = logging.getLogger(__name__)


def includeme(config):
    settings = config.registry.settings

    logger.info('Adding account ...')

    config.add_route('account_login', '/account/login/{protocol}')
    config.add_route('account_logout', '/account/logout')
    config.add_route('account_auth', '/account/auth/{provider_name}')
    config.add_route('account_register', '/account/register')
