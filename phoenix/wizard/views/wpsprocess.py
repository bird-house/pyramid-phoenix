from pyramid.view import view_config
import colander
import deform

from owslib.wps import WebProcessingService

from phoenix.utils import wps_caps_url
from phoenix.wizard.views import Wizard


def includeme(config):
    config.add_route('wizard_process', '/wizard/process')
    config.add_view('phoenix.wizard.views.wpsprocess.ChooseWPSProcess',
                    route_name='wizard_process',
                    attr='view',
                    renderer='../templates/wizard/wpsprocess.pt')


def count_literal_inputs(wps, identifier):
    process = wps.describeprocess(identifier)
    literal_inputs = []
    for inp in process.dataInputs:
        if inp.dataType != 'ComplexData':
            literal_inputs.append(inp)
    return len(literal_inputs)


class Schema(colander.MappingSchema):
    @colander.deferred
    def deferred_validator(node, kw):
        wps = kw.get('wps')

        choices = []
        for process in wps.processes:
            choices.append(process.identifier)
        return colander.OneOf(choices)

    @colander.deferred
    def deferred_widget(node, kw):
        wps = kw.get('wps')

        choices = []
        for process in wps.processes:
            desc = process.title
            if hasattr(process, 'abstract'):
                desc = "{0.title} - {0.abstract}".format(process)
            choices.append((process.identifier, desc))
        return deform.widget.RadioChoiceWidget(values=choices)

    identifier = colander.SchemaNode(
        colander.String(),
        title="Process",
        validator=deferred_validator,
        widget=deferred_widget)


class ChooseWPSProcess(Wizard):
    def __init__(self, request):
        super(ChooseWPSProcess, self).__init__(
            request,
            name='wizard_process',
            title='Choose WPS Process')
        self.wps = WebProcessingService(
            url=request.route_url('owsproxy', service_name=self.wizard_state.get('wizard_wps')['identifier']),
            verify=False)
        self.title = "Choose WPS Process of {0}".format(self.wps.identification.title)

    def breadcrumbs(self):
        breadcrumbs = super(ChooseWPSProcess, self).breadcrumbs()
        breadcrumbs.append(dict(route_path=self.request.route_path(self.name), title=self.title))
        return breadcrumbs

    def schema(self):
        return Schema().bind(wps=self.wps)

    def next_success(self, appstruct):
        self.success(appstruct)

        # TODO: this code does not belong here
        identifier = appstruct['identifier']
        if count_literal_inputs(self.wps, identifier) > 0:
            return self.next('wizard_literal_inputs')
        self.wizard_state.set('wizard_literal_inputs', {})
        return self.next('wizard_complex_inputs')

    def view(self):
        return super(ChooseWPSProcess, self).view()

    def custom_view(self):
        return dict(
            url=wps_caps_url(self.wps.url),
            summary_title=self.wps.identification.title,
            summary=self.wps.identification.abstract,
            provider_name=self.wps.provider.name,
            provider_url=self.wps.provider.url
        )
