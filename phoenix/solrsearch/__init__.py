from pyramid.settings import asbool


def includeme(config):
    settings = config.registry.settings
    if asbool(settings.get('phoenix.solr', 'false')):
        config.add_route('solrsearch', '/solrsearch')
