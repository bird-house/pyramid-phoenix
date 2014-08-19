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

class LiteralInputs(Wizard):
    def __init__(self, request):
        super(LiteralInputs, self).__init__(
            request,
            "Literal Inputs",
            "")
        self.wps = WebProcessingService(self.wizard_state.get('wps_url'))
        self.process = self.wps.describeprocess(self.wizard_state.get('process_identifier'))
        self.description = "Process %s" % self.process.title

    def schema(self):
        from phoenix.wps import WPSSchema
        return WPSSchema(info=False, hide_complex=True, process = self.process)

    def success(self, appstruct):
        self.wizard_state.set('literal_inputs', appstruct)

    def previous_success(self, appstruct):
        self.success(appstruct)
        return self.previous()
    
    def next_success(self, appstruct):
        self.success(appstruct)
        return self.next('wizard_complex_inputs')
    
    def appstruct(self):
        return self.wizard_state.get('literal_inputs', {})

    def breadcrumbs(self):
        breadcrumbs = super(LiteralInputs, self).breadcrumbs()
        breadcrumbs.append(dict(route_name='wizard_literal_inputs', title=self.title))
        return breadcrumbs

    @view_config(route_name='wizard_literal_inputs', renderer='phoenix:templates/wizard/default.pt')
    def view(self):
        return super(LiteralInputs, self).view()
    
