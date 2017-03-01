from pyramid_layout.panel import panel_config


@panel_config(name='esgfsearch', renderer='templates/esgfsearch/panels/search.pt')
def esgfsearch(context, request):
    return dict(
        query="",
        distrib='false',
        replica='false',
        latest='true',
        temporal='true',
        start='2001',
        end='2005',
        facets="")
