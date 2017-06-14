def includeme(config):
    # security
    config.include('phoenix.security')

    # esgf logon views
    config.add_route('esgflogon', '/esgf/logon')
    config.add_view('phoenix.esgf.views.ESGFLogon',
                    route_name='esgflogon',
                    attr='view',
                    renderer='templates/esgf/esgflogon.pt')
    config.add_route('esgflogon_loading', '/esgf/logon/loading')
    config.add_view('phoenix.esgf.views.ESGFLogon',
                    route_name='esgflogon_loading',
                    attr='loading',
                    renderer='templates/esgf/loading.pt')
    config.add_route('esgf_check_logon', '/esgf/check_logon.json')
    config.add_view('phoenix.esgf.views.ESGFLogon',
                    route_name='esgf_check_logon',
                    attr='check_logon',
                    renderer='json')
    # esgf search views
    config.add_route('esgfsearch', '/esgfsearch')
    config.add_view('phoenix.esgf.views.ESGFSearchActions',
                    route_name='esgfsearch',
                    attr='search_datasets',
                    renderer='templates/esgf/esgfsearch.pt')
    config.add_route('esgfsearch_items', '/esgfsearch/items')
    config.add_view('phoenix.esgf.views.ESGFSearchActions',
                    route_name='esgfsearch_items',
                    attr='search_items',
                    renderer='json')

    # shortcuts
    def add_cert_ok(request):
        from phoenix.esgf.validator import cert_ok
        return cert_ok(request)
    config.add_request_method(add_cert_ok, 'cert_ok', reify=True)
