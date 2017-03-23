def includeme(config):
    config.add_route('esgfsearch', '/esgfsearch')
    config.add_view('phoenix.esgfsearch.views.ESGFSearchActions',
                    route_name='esgfsearch',
                    attr='search_datasets',
                    renderer='templates/esgfsearch/esgfsearch.pt')

    config.add_route('esgfsearch_files', '/esgfsearch/files')
    config.add_view('phoenix.esgfsearch.views.ESGFSearchActions',
                    route_name='esgfsearch_files',
                    attr='search_files',
                    renderer='json')

    config.add_route('esgfsearch_aggregations', '/esgfsearch/aggregations')
    config.add_view('phoenix.esgfsearch.views.ESGFSearchActions',
                    route_name='esgfsearch_aggregations',
                    attr='search_aggregations',
                    renderer='json')
