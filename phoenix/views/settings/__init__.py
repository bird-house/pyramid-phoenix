from pyramid.view import view_defaults

from phoenix.views import MyView

import logging
logger = logging.getLogger(__name__)

@view_defaults(permission='admin', layout='default')    
class SettingsView(MyView):
    def __init__(self, request, name, title, description=None):
        super(SettingsView, self).__init__(request, name, title, description)
        self.settings = self.request.registry.settings

    def breadcrumbs(self):
        breadcrumbs = super(SettingsView, self).breadcrumbs()
        breadcrumbs.append(dict(route_path=self.request.route_path('settings'), title="Settings"))
        return breadcrumbs
