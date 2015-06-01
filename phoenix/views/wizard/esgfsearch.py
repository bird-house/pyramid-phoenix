from pyramid.view import view_config

from phoenix.views.wizard import Wizard
from phoenix.models import user_cert_valid

import logging
logger = logging.getLogger(__name__)

class ESGFSearch(Wizard):
    def __init__(self, request):
        super(ESGFSearch, self).__init__(request, name='wizard_esgf_search', title="ESGF Search")

    def breadcrumbs(self):
        breadcrumbs = super(ESGFSearch, self).breadcrumbs()
        breadcrumbs.append(dict(route_path=self.request.route_path(self.name), title=self.title))
        return breadcrumbs

    def schema(self):
        from phoenix.schema import ESGFSearchSchema
        return ESGFSearchSchema()

    def next_success(self, appstruct):
        self.success(appstruct)

        # TODO: need to check pre conditions in wizard
        if user_cert_valid(self.request):
            return self.next('wizard_done')
        return self.next('wizard_esgf_login')

    @view_config(route_name='wizard_esgf_search', renderer='phoenix:templates/wizard/esgfsearch.pt')
    def view(self):
        return super(ESGFSearch, self).view()
