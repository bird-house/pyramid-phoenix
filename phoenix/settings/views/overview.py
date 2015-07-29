from pyramid.view import view_config

from . import SettingsView

import logging
logger = logging.getLogger(__name__)

class Overview(SettingsView):
    def __init__(self, request):
        super(Overview, self).__init__(request, name='settings', title='Overview')

    @view_config(route_name='settings', renderer='../templates/settings/overview.pt')
    def view(self):
        buttongroups = []
        buttons = []

        buttons.append(dict(url=self.request.route_path('supervisor'), icon="monitor_edit.png", title="Supervisor"))
        buttons.append(dict(url=self.request.route_path('services'), icon="bookshelf.png", title="Services"))
        buttons.append(dict(url=self.request.route_path('settings_solr', tab='index'), icon="solr.png", title="Solr"))
        buttons.append(dict(url=self.request.route_path('settings_users'), icon="user_catwomen.png", title="Users"))
        buttons.append(dict(url=self.settings.get('celery.url'), icon="celery_128.png", title="Celery", id="external-url"))
        buttons.append(dict(url=self.request.route_path('settings_monitor'), icon="blackboard_sum.png", title="Monitor"))
        buttons.append(dict(url=self.request.route_path('settings_auth'), icon="lock_edit.png", title="Auth"))
        buttons.append(dict(url=self.request.route_path('settings_ldap'), icon="ldap.png", title="LDAP"))
        buttongroups.append(dict(title='Settings', buttons=buttons))

        return dict(buttongroups=buttongroups)
