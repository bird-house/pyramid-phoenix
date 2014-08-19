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

class ChooseWPS(Wizard):
    def __init__(self, request):
        super(ChooseWPS, self).__init__(request, 'WPS')
        self.description = "Choose Web Processing Service"

    def schema(self):
        from phoenix.schema import ChooseWPSSchema
        return ChooseWPSSchema().bind(wps_list = models.get_wps_list(self.request))

    def success(self, appstruct):
        self.wizard_state.set('wps_url', appstruct.get('url'))

    def previous_success(self, appstruct):
        self.success(appstruct)
        return self.previous()

    def next_success(self, appstruct):
        self.success(appstruct)
        return self.next('wizard_process')

    def appstruct(self):
        return dict(url=self.wizard_state.get('wps_url'))

    @view_config(route_name='wizard_wps', renderer='phoenix:templates/wizard/default.pt')
    def view(self):
        return super(ChooseWPS, self).view()
    
