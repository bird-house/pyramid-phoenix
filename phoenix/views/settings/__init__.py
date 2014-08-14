from pyramid.view import view_defaults

from phoenix.view import MyView

import logging
logger = logging.getLogger(__name__)

@view_defaults(permission='admin', layout='default')    
class SettingsView(MyView):
    def __init__(self, request, title="Settings", description=None):
        super(SettingsView, self).__init__(request, title, description)
        self.settings = self.request.registry.settings

    def breadcrumbs(self):
        breadcrumbs = super(SettingsView, self).breadcrumbs()
        breadcrumbs.append(dict(route_name='settings', title="Settings"))
        return breadcrumbs
