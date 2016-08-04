from pyramid.view import view_config

from . import SettingsView

import logging
logger = logging.getLogger(__name__)


class Overview(SettingsView):
    def __init__(self, request):
        super(Overview, self).__init__(request, name='settings', title='Overview')

    @view_config(route_name='settings', renderer='../templates/settings/overview.pt')
    def view(self):
        buttongroups = list()
        buttons = list()

        buttons.append(dict(url=self.request.route_path('supervisor'), icon_class="fa fa-eye fa-2x", title="Supervisor"))
        buttons.append(dict(url=self.request.route_path('services'), icon_class="fa fa-server fa-2x", title="Services"))
        if self.request.solr_activated:
            buttons.append(dict(url=self.request.route_path('settings_solr', tab='index'), icon_class="fa fa-search fa-2x", title="Solr"))
        buttons.append(dict(url=self.request.route_path('settings_auth'), icon_class="fa fa-lock fa-2x", title="Auth"))
        buttons.append(dict(url=self.request.route_path('settings_ldap'), icon_class="fa fa-sitemap fa-2x", title="LDAP"))
        buttons.append(dict(url=self.request.route_path('settings_github'), icon_class="fa fa-github fa-2x", title="GitHub"))
        buttongroups.append(dict(title='Settings', buttons=buttons))

        return dict(buttongroups=buttongroups)
