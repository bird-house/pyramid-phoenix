import os
from pyramid.view import view_config, view_defaults

from mako.template import Template

from phoenix.views import MyView


import logging
logger = logging.getLogger(__name__)

solrsearch_script = Template(
    filename=os.path.join(os.path.dirname(__file__), "..", "templates", "solrsearch", "solrsearch.js"),
    output_encoding="utf-8", input_encoding="utf-8")


@view_defaults(permission='view', layout='default')
class SolrSearch(MyView):
    def __init__(self, request):
        super(SolrSearch, self).__init__(request, name='solrsearch', title='Solrsearch')

    @view_config(route_name='solrsearch', renderer='../templates/solrsearch/solrsearch.pt')
    def view(self):
        query = self.request.params.get('q', '')
        page = int(self.request.params.get('page', '0'))

        lm = self.request.layout_manager
        lm.layout.add_heading('solrsearch')

        return dict(solrsearch_script=solrsearch_script.render(request=self.request, query=query, page=page))


