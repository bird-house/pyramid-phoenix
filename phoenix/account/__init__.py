import logging
LOGGER = logging.getLogger("PHOENIX")


def includeme(config):
    settings = config.registry.settings

    config.add_route('sign_in', '/account/login')
    config.add_route('esgf_login', '/account/login/esgf')
    config.add_route('ldap_login', '/account/login/ldap')
    config.add_route('account_logout', '/account/logout')
    config.add_route('account_auth', '/account/auth/{provider}')
    config.add_route('account_register', '/account/register')

    def github_activated(request):
        settings = request.registry.settings
        return len(settings.get('github.client.id', '').strip()) >= 10
    config.add_request_method(github_activated, reify=True)
