def includeme(config):
    config.add_route('esgfsearch', '/esgfsearch')
    config.add_view('phoenix.esgfsearch.views.ESGFSearch',
                    route_name='esgfsearch',
                    attr='view',
                    renderer='templates/esgfsearch/esgfsearch.pt')
