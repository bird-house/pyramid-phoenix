from pyramid.view import view_config
from pyramid.settings import asbool

from phoenix.wizard.views import Wizard
from phoenix.esgf.validator import cert_ok
from phoenix.esgf.schema import ESGFSearchSchema
from phoenix.esgf.search import ESGFSearch

import logging
LOGGER = logging.getLogger("PHOENIX")


def includeme(config):
    config.add_route('wizard_esgf_search', '/wizard/esgfsearch')
    config.add_view('phoenix.wizard.views.esgfsearch.ESGFSearchView',
                    route_name='wizard_esgf_search',
                    attr='view',
                    renderer='phoenix.esgf:templates/esgf/esgfsearch.pt')


class ESGFSearchView(Wizard):
    def __init__(self, request):
        super(ESGFSearchView, self).__init__(request, name='wizard_esgf_search', title="ESGF Search")
        self.esgfsearch = ESGFSearch(self.request)

    def breadcrumbs(self):
        breadcrumbs = super(ESGFSearchView, self).breadcrumbs()
        breadcrumbs.append(dict(route_path=self.request.route_path(self.name), title=self.title))
        return breadcrumbs

    def schema(self):
        return ESGFSearchSchema()

    def appstruct(self):
        appstruct = super(ESGFSearchView, self).appstruct()
        # TODO: not so nice to update appstruct like this
        appstruct.update(self.esgfsearch.params())
        LOGGER.debug("esgfsearch appstruct before: %s", appstruct)
        return appstruct

    def next_ok(self):
        return cert_ok(self.request)

    def next_success(self, appstruct):
        LOGGER.debug("esgfsearch appstruct after: %s", appstruct)
        self.success(appstruct)
        return self.next('wizard_done')

    def custom_view(self):
        result = dict()
        result.update(self.esgfsearch.query_params())
        result.update(self.esgfsearch.search_datasets())
        result['quickview'] = False
        return result
