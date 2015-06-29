from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from phoenix.settings.views import SettingsView

import logging
logger = logging.getLogger(__name__)

class Auth(SettingsView):
    def __init__(self, request):
        super(Auth, self).__init__(request, name='settings_auth', title='auth')

    def breadcrumbs(self):
        breadcrumbs = super(Auth, self).breadcrumbs()
        breadcrumbs.append(dict(route_path=self.request.route_path(self.name), title=self.title))
        return breadcrumbs

    @view_config(route_name='settings_auth', renderer='../templates/settings/auth.pt')
    def view(self):
        return dict()


