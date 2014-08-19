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

class StartWizard(Wizard):
    def __init__(self, request):
        super(StartWizard, self).__init__(request, 'Wizard')
        self.description = "Choose Favorite or None."
        self.wizard_state.clear()

    def schema(self):
        from phoenix.schema import WizardSchema
        return WizardSchema().bind(favorites=self.favorite.names())

    def success(self, appstruct):
        favorite_state = self.favorite.get(appstruct.get('favorite', 'None'))
        self.wizard_state.load(favorite_state)
        self.wizard_state.set('wizard', appstruct)

    def previous_success(self, appstruct):
        self.success(appstruct)
        return self.previous()

    def next_success(self, appstruct):
        self.success(appstruct)
        return self.next('wizard_wps')

    def appstruct(self):
        return self.wizard_state.get('wizard', {})

    @view_config(route_name='wizard', renderer='phoenix:templates/wizard/default.pt')
    def view(self):
        return super(StartWizard, self).view()
