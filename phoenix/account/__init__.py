from pyramid.settings import asbool

import logging
LOGGER = logging.getLogger("PHOENIX")


def includeme(config):
    config.add_route('sign_in', '/account/login')
    config.add_route('account_logout', '/account/logout')
    config.add_route('account_auth', '/account/auth/{provider}')
    config.add_route('account_register', '/account/register')

    def keycloak_activated(request):
        settings = request.registry.settings
        return len(settings.get('keycloak.client.id', '').strip()) >= 2
    config.add_request_method(keycloak_activated, reify=True)

    def github_activated(request):
        settings = request.registry.settings
        return len(settings.get('github.client.id', '').strip()) >= 10
    config.add_request_method(github_activated, reify=True)

    def ceda_oauth_activated(request):
        settings = request.registry.settings
        return len(settings.get('ceda.client.id', '').strip()) >= 10
    config.add_request_method(ceda_oauth_activated, reify=True)
