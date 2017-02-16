from pyramid.view import view_config

from owslib.wps import WebProcessingService

from phoenix.wizard.views import Wizard
from phoenix.wps import WPSSchema
from phoenix.utils import wps_describe_url

import logging
logger = logging.getLogger(__name__)


def includeme(config):
    config.add_route('wizard_literal_inputs', '/wizard/literal_inputs')
    config.add_view('phoenix.wizard.views.literalinputs.LiteralInputs',
                    route_name='wizard_literal_inputs',
                    attr='view',
                    renderer='../templates/wizard/inputs.pt')


class LiteralInputs(Wizard):
    def __init__(self, request):
        super(LiteralInputs, self).__init__(request, name='wizard_literal_inputs', title="Literal Inputs")
        self.wps = WebProcessingService(
            url=request.route_url('owsproxy', service_name=self.wizard_state.get('wizard_wps')['identifier']),
            verify=False, skip_caps=True)
        self.process = self.wps.describeprocess(self.wizard_state.get('wizard_process')['identifier'])
        self.title = "Literal inputs of {0}".format(self.process.title)

    def breadcrumbs(self):
        breadcrumbs = super(LiteralInputs, self).breadcrumbs()
        breadcrumbs.append(dict(route_path=self.request.route_path(self.name), title=self.title))
        return breadcrumbs

    def schema(self):
        return WPSSchema(request=self.request, hide_complex=True, process=self.process)

    def next_success(self, appstruct):
        self.success(appstruct)
        return self.next('wizard_complex_inputs')

    def view(self):
        return super(LiteralInputs, self).view()

    def custom_view(self):
        return dict(
            summary_title=self.process.title,
            summary=getattr(self.process, 'abstract', 'No summary'),
            url=wps_describe_url(self.wps.url, self.process.identifier),
            metadata=self.process.metadata)
