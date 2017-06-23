from pyramid.settings import asbool


def includeme(config):
    if asbool(settings.get('phoenix.solr', 'false')):
        config.add_route('solrsearch', '/solrsearch')
