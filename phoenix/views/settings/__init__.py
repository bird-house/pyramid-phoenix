from pyramid.view import view_defaults

from phoenix.view import MyView

import logging
logger = logging.getLogger(__name__)

@view_defaults(permission='admin', layout='default')    
class SettingsView(MyView):
    def __init__(self, request, title="Settings", description=None):
        super(SettingsView, self).__init__(request, title, description)
        self.settings = self.request.registry.settings
        self.top_title = "Settings"
        self.top_route_name = "settings"
