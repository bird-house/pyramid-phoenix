from pyramid.view import view_config

from . import SettingsView

import logging
logger = logging.getLogger(__name__)

class SupervisorLog(SettingsView):
    def __init__(self, request):
        super(SupervisorLog, self).__init__(request, name='supervisor_log', title='Log')
        
    def breadcrumbs(self):
        breadcrumbs = super(SupervisorLog, self).breadcrumbs()
        breadcrumbs.append(dict(route_path=self.request.route_path('settings_supervisor'), title='Supervisor'))
        breadcrumbs.append(dict(route_path=self.request.current_route_path(), title=self.title))
        return breadcrumbs

    @view_config(route_name='supervisor_log', renderer='../templates/settings/supervisor_log.pt')
    def view(self):
        import xmlrpclib
        self.server = xmlrpclib.Server('http://localhost:9001/RPC2')
        name = self.request.matchdict.get('name')
        #offset = self.request.matchdict.get('offset')
        
        log = self.server.supervisor.tailProcessStdoutLog(name, 0, 4096)
        log_list = log[0].split('\n')
        #offset = max(0, log[1] - 1024)
        return dict(name=name, log=log_list)

