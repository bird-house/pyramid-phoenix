from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound

from deform import Form, Button

from owslib.wps import WebProcessingService

from string import Template

from phoenix import models
from phoenix.views import MyView
from phoenix.grid import MyGrid
from phoenix.views.wizard import Wizard
from phoenix.exceptions import MyProxyLogonFailure

class ESGFSearch(Wizard):
    def __init__(self, request):
        super(ESGFSearch, self).__init__(
            request,
            "ESGF Search",
            "")

    def schema(self):
        from phoenix.schema import ESGFSearchSchema
        return ESGFSearchSchema()

    def success(self, appstruct):
        self.wizard_state.set('esgf_selection', appstruct.get('selection'))

    def previous_success(self, appstruct):
        self.success(appstruct)
        return self.previous()
        
    def next_success(self, appstruct):
        self.success(appstruct)
        return self.next('wizard_esgf_files')

    def appstruct(self):
        return dict(selection=self.wizard_state.get('esgf_selection', {}))

    def breadcrumbs(self):
        breadcrumbs = super(ESGFSearch, self).breadcrumbs()
        breadcrumbs.append(dict(route_name='wizard_esgf', title=self.title))
        return breadcrumbs

    @view_config(route_name='wizard_esgf', renderer='phoenix:templates/wizard/esgf.pt')
    def view(self):
        return super(ESGFSearch, self).view()
