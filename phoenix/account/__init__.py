import logging
LOGGER = logging.getLogger("PHOENIX")


def includeme(config):
    settings = config.registry.settings

    config.add_route('sign_in', '/account/sign_in')
    config.add_route('account_login', '/account/login/{protocol}')
    config.add_route('account_logout', '/account/logout')
    config.add_route('account_auth', '/account/auth/{provider_name}')
    config.add_route('account_register', '/account/register')
