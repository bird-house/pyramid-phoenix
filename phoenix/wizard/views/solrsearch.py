from pyramid.view import view_config

import colander

from phoenix.solrsearch.schema import SolrSearchSchema
from phoenix.wizard.views import Wizard

import logging
logger = logging.getLogger(__name__)


def includeme(config):
    config.add_route('wizard_solr', '/wizard/solrsearch')


class SolrSearch(Wizard):
    def __init__(self, request):
        super(SolrSearch, self).__init__(request, name='wizard_solr', title="Solr Search")

    def breadcrumbs(self):
        breadcrumbs = super(SolrSearch, self).breadcrumbs()
        breadcrumbs.append(dict(route_path=self.request.route_path(self.name), title=self.title))
        return breadcrumbs

    def schema(self):
        return SolrSearchSchema()

    def appstruct(self):
        appstruct = super(SolrSearch, self).appstruct()
        appstruct['query'] = self.request.params.get('q', colander.null)
        appstruct['category'] = self.request.params.get('category', colander.null)
        appstruct['source'] = self.request.params.get('source', colander.null)
        return appstruct

    def next_success(self, appstruct):
        self.success(appstruct)
        return self.next('wizard_done')

    def custom_view(self):
        query = self.request.params.get('q', '')
        page = int(self.request.params.get('page', '0'))

        lm = self.request.layout_manager
        lm.layout.add_heading('solrsearch')

        return dict()

    @view_config(route_name='wizard_solr', renderer='../templates/wizard/solrsearch.pt')
    def view(self):
        return super(SolrSearch, self).view()
