from pyramid.view import view_config
import colander
import deform

from phoenix.wizard.views import Wizard
from phoenix.utils import wps_url

@colander.deferred
def deferred_choose_input_parameter_widget(node, kw):
    process = kw.get('process', [])

    choices = []
    for dataInput in process.dataInputs:
        if dataInput.dataType == 'ComplexData':
            title = dataInput.title
            title += " [%s]" % (', '.join([value.mimeType for value in dataInput.supportedValues]))
            choices.append( (dataInput.identifier, title) )
    return deform.widget.RadioChoiceWidget(values = choices)

class ChooseInputParamterSchema(colander.MappingSchema):
    identifier = colander.SchemaNode(
        colander.String(),
        title = "Input Parameter",
        widget = deferred_choose_input_parameter_widget)

class ComplexInputs(Wizard):
    def __init__(self, request):
        super(ComplexInputs, self).__init__(
            request, name='wizard_complex_inputs',
            title="Choose Complex Input Parameter")
        from owslib.wps import WebProcessingService
        self.wps = WebProcessingService(wps_url(request, self.wizard_state.get('wizard_wps')['identifier']))
        self.process = self.wps.describeprocess(self.wizard_state.get('wizard_process')['identifier'])
        self.description = "Process %s" % self.process.title

    def breadcrumbs(self):
        breadcrumbs = super(ComplexInputs, self).breadcrumbs()
        breadcrumbs.append(dict(route_path=self.request.route_path(self.name), title=self.title))
        return breadcrumbs

    def schema(self):
        return ChooseInputParamterSchema().bind(process=self.process)

    def success(self, appstruct):
        for input in self.process.dataInputs:
            if input.identifier == appstruct.get('identifier'):
                appstruct['mime_types'] = [value.mimeType for value in input.supportedValues]
        super(ComplexInputs, self).success(appstruct)

    def next_success(self, appstruct):
        self.success(appstruct)
        return self.next('wizard_source')

    @view_config(route_name='wizard_complex_inputs', renderer='../templates/wizard/default.pt')
    def view(self):
        return super(ComplexInputs, self).view()
