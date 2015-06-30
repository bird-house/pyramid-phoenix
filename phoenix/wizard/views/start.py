from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from phoenix.wizard.views import Wizard

import logging
logger = logging.getLogger(__name__)

import colander
from deform.widget import SelectWidget
class Schema(colander.MappingSchema):
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
        super(Start, self).__init__(request, name='wizard', title='Choose a Favorite')
        self.wizard_state.clear()
        self.favorite.load()

    def schema(self):
        return Schema().bind(favorites=self.favorite.names())

    def success(self, appstruct):
        favorite_state = self.favorite.get(appstruct.get('favorite'))
        self.wizard_state.load(favorite_state)
        super(Start, self).success(appstruct)

    def next_success(self, appstruct):
        self.success(appstruct)
        return self.next('wizard_wps')

    @view_config(route_name='wizard_clear_favorites')
    def clear_favorites(self):
        self.favorite.drop()
        return HTTPFound(location=self.request.route_path('wizard'))

    @view_config(route_name='wizard', renderer='../templates/wizard/start.pt')
    def view(self):
        return super(Start, self).view()
