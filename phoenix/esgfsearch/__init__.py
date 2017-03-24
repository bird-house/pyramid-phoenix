def includeme(config):
    config.add_route('esgfsearch', '/esgfsearch')
    config.add_view('phoenix.esgfsearch.views.ESGFSearchActions',
                    route_name='esgfsearch',
                    attr='search_datasets',
                    renderer='templates/esgfsearch/esgfsearch.pt')
    config.add_route('esgfsearch_items', '/esgfsearch/items')
    config.add_view('phoenix.esgfsearch.views.ESGFSearchActions',
                    route_name='esgfsearch_items',
                    attr='search_items',
                    renderer='json')
