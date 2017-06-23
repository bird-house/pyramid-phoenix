from pyramid.settings import asbool


def includeme(config):
    settings = config.registry.settings
    if asbool(settings.get('phoenix.solr', 'false')):
        # solr search view
        config.add_route('solrsearch', '/solrsearch')
        config.add_view('phoenix.solrsearch.views.SolrSearch',
                        route_name='solrsearch',
                        attr='view',
                        renderer='templates/solrsearch/solrsearch.pt')
