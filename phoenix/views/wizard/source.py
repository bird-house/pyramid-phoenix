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

class ChooseSource(Wizard):
    def __init__(self, request):
        super(ChooseSource, self).__init__(
            request,
            "Choose Source",
            "")
        self.description = self.wizard_state.get('complex_input_identifier')
    def schema(self):
        from phoenix.schema import ChooseSourceSchema
        return ChooseSourceSchema()

    def success(self, appstruct):
        self.wizard_state.set('source', appstruct.get('source'))

    def previous_success(self, appstruct):
        self.success(appstruct)
        return self.previous()

    def next_success(self, appstruct):
        self.success(appstruct)
        return self.next( self.wizard_state.get('source') )
        
    def appstruct(self):
        return dict(source=self.wizard_state.get('source'))

    def breadcrumbs(self):
        breadcrumbs = super(ChooseSource, self).breadcrumbs()
        breadcrumbs.append(dict(route_name='wizard_source', title=self.title))
        return breadcrumbs

    @view_config(route_name='wizard_source', renderer='phoenix:templates/wizard/default.pt')
    def view(self):
        return super(ChooseSource, self).view()
    
