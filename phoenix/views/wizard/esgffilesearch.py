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

class ESGFFileSearch(Wizard):
    def __init__(self, request):
        super(ESGFFileSearch, self).__init__(
            request,
            "ESGF File Search",
            "")

    def schema(self):
        from phoenix.schema import ESGFFilesSchema
        return ESGFFilesSchema().bind(selection=self.wizard_state.get('esgf_selection'))

    def success(self, appstruct):
        self.wizard_state.set('esgf_files', appstruct.get('url'))

    def previous_success(self, appstruct):
        self.success(appstruct)
        return self.previous()
        
    def next_success(self, appstruct):
        self.success(appstruct)
        return self.next('wizard_esgf_credentials')
        
    def appstruct(self):
        return dict(url=self.wizard_state.get('esgf_files'))

    def breadcrumbs(self):
        breadcrumbs = super(ESGFFileSearch, self).breadcrumbs()
        breadcrumbs.append(dict(route_name='wizard_esgf_files', title=self.title))
        return breadcrumbs

    @view_config(route_name='wizard_esgf_files', renderer='phoenix:templates/wizard/esgf.pt')
    def view(self):
        return super(ESGFFileSearch, self).view()
