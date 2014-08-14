from pyramid.view import view_config, view_defaults

from pyramid.httpexceptions import HTTPException, HTTPFound, HTTPNotFound
from deform import Form, Button
from deform import ValidationFailure

from phoenix.view import MyView

import logging
logger = logging.getLogger(__name__)

@view_defaults(permission='admin', layout='default')    
class SettingsView(MyView):
    def __init__(self, request, title="Settings", description=None):
        super(SettingsView, self).__init__(request, title, description)
        self.settings = self.request.registry.settings
        self.top_title = "Settings"
        self.top_route_name = "all_settings"

class AllSettings(SettingsView):
    def __init__(self, request):
        super(AllSettings, self).__init__(request, 'All Settings')
        self.settings = self.request.registry.settings

    @view_config(route_name='all_settings', renderer='phoenix:templates/settings/all.pt')
    def view(self):
        buttongroups = []
        buttons = []

        buttons.append(dict(url=self.settings.get('supervisor.url'),
                            icon="monitor_edit.png", title="Supervisor", id="external-url"))
        buttons.append(dict(url="/settings/catalog", icon="catalog_pages.png", title="Catalog"))
        buttons.append(dict(url="/settings/users", icon="user_catwomen.png", title="Users"))
        buttons.append(dict(url=self.settings.get('thredds.url'),
                            icon="unidataLogo.png", title="Thredds", id="external-url"))
        buttongroups.append(dict(title='Settings', buttons=buttons))

        return dict(buttongroups=buttongroups)

