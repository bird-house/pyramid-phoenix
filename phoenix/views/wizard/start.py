from pyramid.view import view_config

from phoenix.views.wizard import Wizard

import logging
logger = logging.getLogger(__name__)

import colander
from deform.widget import SelectWidget
class WizardSchema(colander.MappingSchema):
    @colander.deferred
    def deferred_favorite_widget(node, kw):
        favorites = kw.get('favorites', ['No Favorite'])
        choices = [(item, item) for item in favorites]
        return SelectWidget(values = choices)

    favorite = colander.SchemaNode(
        colander.String(),
        widget = deferred_favorite_widget)

class Start(Wizard):
    def __init__(self, request):
        super(Start, self).__init__(request, name='wizard', title='Start')
        self.description = "Choose Favorite or None."
        self.wizard_state.clear()

    def schema(self):
        return WizardSchema().bind(favorites=self.favorite.names())

    def success(self, appstruct):
        favorite_state = self.favorite.get(appstruct.get('favorite'))
        self.wizard_state.load(favorite_state)
        super(Start, self).success(appstruct)

    def next_success(self, appstruct):
        self.success(appstruct)
        return self.next('wizard_wps')

    @view_config(route_name='wizard', renderer='phoenix:templates/wizard/default.pt')
    def view(self):
        return super(Start, self).view()
