from pyramid.settings import asbool

def includeme(config):
    settings = config.registry.settings

    if asbool(settings.get('phoenix.ldap', 'false')):
        config.include('pyramid_ldap')
