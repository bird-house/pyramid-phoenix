from pyramid.view import view_config

from phoenix.wizard.views import Wizard
from phoenix.catalog import wps_url

class LiteralInputs(Wizard):
    def __init__(self, request):
        super(LiteralInputs, self).__init__(request, name='wizard_literal_inputs', title="Literal Inputs")
        from owslib.wps import WebProcessingService
        self.wps = WebProcessingService(wps_url(request, self.wizard_state.get('wizard_wps')['identifier']))
        self.process = self.wps.describeprocess(self.wizard_state.get('wizard_process')['identifier'])
        self.title = "Literal inputs of {0}".format(self.process.title)

    def breadcrumbs(self):
        breadcrumbs = super(LiteralInputs, self).breadcrumbs()
        breadcrumbs.append(dict(route_path=self.request.route_path(self.name), title=self.title))
        return breadcrumbs

    def schema(self):
        from phoenix.schema.wps import WPSSchema
        return WPSSchema(hide_complex=True, process = self.process)

    def next_success(self, appstruct):
        self.success(appstruct)
        return self.next('wizard_complex_inputs')
    
    @view_config(route_name='wizard_literal_inputs', renderer='../templates/wizard/default.pt')
    def view(self):
        return super(LiteralInputs, self).view()
    
