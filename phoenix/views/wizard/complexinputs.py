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

class ComplexInputs(Wizard):
    def __init__(self, request):
        super(ComplexInputs, self).__init__(
            request,
            "Choose Complex Input Parameter",
            "")
        self.wps = WebProcessingService(self.wizard_state.get('wps_url'))
        self.process = self.wps.describeprocess(self.wizard_state.get('process_identifier'))
        self.description = "Process %s" % self.process.title

    def schema(self):
        from phoenix.schema import ChooseInputParamterSchema
        return ChooseInputParamterSchema().bind(process=self.process)

    def success(self, appstruct):
        self.wizard_state.set('complex_input_identifier', appstruct.get('identifier'))
        for input in self.process.dataInputs:
            if input.identifier == appstruct.get('identifier'):
                self.wizard_state.set('mime_types', [value.mimeType for value in input.supportedValues])

    def previous_success(self, appstruct):
        self.success(appstruct)
        return self.previous()

    def next_success(self, appstruct):
        self.success(appstruct)
        return self.next('wizard_source')

    def appstruct(self):
        return dict(identifier=self.wizard_state.get('complex_input_identifier'))

    def breadcrumbs(self):
        breadcrumbs = super(ComplexInputs, self).breadcrumbs()
        breadcrumbs.append(dict(route_name='wizard_complex_inputs', title=self.title))
        return breadcrumbs

    @view_config(route_name='wizard_complex_inputs', renderer='phoenix:templates/wizard/default.pt')
    def view(self):
        return super(ComplexInputs, self).view()
