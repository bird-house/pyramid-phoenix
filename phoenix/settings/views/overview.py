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

        buttons.append(dict(url=self.request.route_path('settings_supervisor'), icon="monitor_edit.png", title="Supervisor"))
        buttons.append(dict(url="/settings/catalog", icon="bookshelf.png", title="Catalog"))
        buttons.append(dict(url="/settings/users", icon="user_catwomen.png", title="Users"))
        buttons.append(dict(url=self.settings.get('celery.url'),
                            icon="celery_128.png", title="Celery", id="external-url"))
        buttons.append(dict(url="/settings/jobs", icon="blackboard_sum.png", title="Monitor"))
        buttons.append(dict(url="/ipython/notebook", icon="ipynb_icon_64x64.png", title="IPython"))
        buttons.append(dict(url=self.settings.get('thredds.url'),
                            icon="unidataLogo.png", title="Thredds", id="external-url"))
        buttongroups.append(dict(title='Settings', buttons=buttons))

        return dict(buttongroups=buttongroups)
