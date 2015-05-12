from pyramid.view import view_config

from phoenix.views.wizard import Wizard

class ComplexInputs(Wizard):
    def __init__(self, request):
        super(ComplexInputs, self).__init__(
            request, name='wizard_complex_inputs',
            title="Choose Complex Input Parameter")
        from owslib.wps import WebProcessingService
        self.wps = WebProcessingService(self.wizard_state.get('wizard_wps')['url'])
        self.process = self.wps.describeprocess(self.wizard_state.get('wizard_process')['identifier'])
        self.description = "Process %s" % self.process.title

    def breadcrumbs(self):
        breadcrumbs = super(ComplexInputs, self).breadcrumbs()
        breadcrumbs.append(dict(route_path=self.request.route_path(self.name), title=self.title))
        return breadcrumbs

    def schema(self):
        from phoenix.schema import ChooseInputParamterSchema
        return ChooseInputParamterSchema().bind(process=self.process)

    def success(self, appstruct):
        for input in self.process.dataInputs:
            if input.identifier == appstruct.get('identifier'):
                appstruct['mime_types'] = [value.mimeType for value in input.supportedValues]
        super(ComplexInputs, self).success(appstruct)

    def next_success(self, appstruct):
        self.success(appstruct)
        return self.next('wizard_source')

    @view_config(route_name='wizard_complex_inputs', renderer='phoenix:templates/wizard/default.pt')
    def view(self):
        return super(ComplexInputs, self).view()
