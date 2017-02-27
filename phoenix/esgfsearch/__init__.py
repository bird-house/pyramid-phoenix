def includeme(config):
    config.add_route('esgfsearch', '/esgfsearch')
    config.add_view('phoenix.esgfsearch.views.ESGFSearch',
                    route_name='esgfsearch',
                    attr='view',
                    renderer='templates/esgfsearch/esgfsearch.pt')

    config.add_route('esgfsearch_search', '/esgfsearch/search')
    config.add_view('phoenix.esgfsearch.views.actions.Actions',
                    route_name='esgfsearch_search',
                    attr='search',
                    renderer='json')
