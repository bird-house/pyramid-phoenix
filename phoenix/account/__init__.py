import logging
LOGGER = logging.getLogger("PHOENIX")


def includeme(config):
    settings = config.registry.settings

    config.add_route('sign_in', '/account/sign_in')
    config.add_route('esgf_login', '/account/login/esgf')
    config.add_route('github_login', '/account/login/github')
    config.add_route('ldap_login', '/account/login/ldap')
    config.add_route('account_logout', '/account/logout')
    config.add_route('account_auth', '/account/auth/{provider}')
    config.add_route('account_register', '/account/register')
