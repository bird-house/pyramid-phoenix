from pyramid.view import view_config

from phoenix.views.wizard import Wizard

class CheckParameters(Wizard):
    def __init__(self, request):
        super(CheckParameters, self).__init__(
            request, name='wizard_check_parameters', title="Check Parameters")
        from owslib.wps import WebProcessingService
        self.wps = WebProcessingService(self.wizard_state.get('wizard_wps')['url'])
        self.process = self.wps.describeprocess(self.wizard_state.get('wizard_process')['identifier'])
        self.description = "Process %s" % self.process.title

    def schema(self):
        from phoenix.schema import NoSchema
        return NoSchema()

    def next_success(self, appstruct):
        return self.next('wizard_done')
        
    def custom_view(self):
        items = []
        for identifier, value in self.wizard_state.get('wizard_literal_inputs', {}).items():
            items.append(dict(title=identifier, value=value))
        identifier=self.wizard_state.get('wizard_complex_inputs')['identifier']
        items.append(dict(title=identifier, format="application/x-netcdf", value=[]))
        grid = CheckParametersGrid(
                self.request,
                items,
                ['input', 'value'],
            )
        return dict(grid=grid)

    @view_config(route_name='wizard_check_parameters', renderer='phoenix:templates/wizard/check.pt')
    def view(self):
        return super(CheckParameters, self).view()
        
from phoenix.grid import MyGrid

class CheckParametersGrid(MyGrid):
    def __init__(self, request, *args, **kwargs):
        super(CheckParametersGrid, self).__init__(request, *args, **kwargs)
        self.column_formats['input'] = self.input_td

    def input_td(self, col_num, i, item):
        return self.render_title_td(
            title=item.get('title'),
            format=item.get('format')
            )

