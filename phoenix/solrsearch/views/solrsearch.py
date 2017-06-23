from pyramid.view import view_config, view_defaults

from phoenix.views import MyView


@view_defaults(permission='view', layout='default')
class SolrSearch(MyView):
    def __init__(self, request):
        super(SolrSearch, self).__init__(request, name='solrsearch', title='Solrsearch')

    @view_config(route_name='solrsearch', renderer='../templates/solrsearch/solrsearch.pt')
    def view(self):
        return dict()
