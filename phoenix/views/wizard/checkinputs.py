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

class CheckParameters(Wizard):
    def __init__(self, request):
        super(CheckParameters, self).__init__(
            request,
            "Check Parameters",
            "")
        self.wps = WebProcessingService(self.wizard_state.get('wps_url'))
        self.process = self.wps.describeprocess(self.wizard_state.get('process_identifier'))
        self.description = "Process %s" % self.process.title

    def schema(self):
        from phoenix.schema import NoSchema
        return NoSchema()

    def success(self, appstruct):
        pass

    def previous_success(self, appstruct):
        return self.previous()
        
    def next_success(self, appstruct):
        return self.next('wizard_done')
        
    def appstruct(self):
        return dict(identifier=self.wizard_state.get('complex_input_identifier'))

    def breadcrumbs(self):
        breadcrumbs = super(CheckParameters, self).breadcrumbs()
        breadcrumbs.append(dict(route_name='wizard_check_parameters', title=self.title))
        return breadcrumbs

    def custom_view(self):
        items = []
        for identifier, value in self.wizard_state.get('literal_inputs', {}).items():
            items.append(dict(title=identifier, value=value))
        identifier=self.wizard_state.get('complex_input_identifier', 'unknown')
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

