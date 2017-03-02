from pyramid_layout.panel import panel_config


@panel_config(name='esgfsearch', renderer='templates/esgfsearch/panels/search.pt')
def esgfsearch(context, request):
    return dict(
        query=request.params.get('query', ''),
        distrib=request.params.get('distrib', 'false'),
        replica=request.params.get('replica', 'false'),
        latest=request.params.get('latest', 'true'),
        temporal=request.params.get('temporal', 'true'),
        start=request.params.get('start', '2001'),
        end=request.params.get('end', '2005'),
        facets=request.params.get('facets', ''))
