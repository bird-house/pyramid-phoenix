from pyramid.view import view_config

from phoenix.settings.views import SettingsView

import logging
logger = logging.getLogger(__name__)

class SupervisorLog(SettingsView):
    def __init__(self, request):
        super(SupervisorLog, self).__init__(request, name='supervisor_log', title='Log')
        
    def breadcrumbs(self):
        breadcrumbs = super(SupervisorLog, self).breadcrumbs()
        breadcrumbs.append(dict(route_path=self.request.route_path('supervisor'), title='Supervisor'))
        breadcrumbs.append(dict(route_path=self.request.current_route_path(), title=self.title))
        return breadcrumbs

    @view_config(route_name='supervisor_log', renderer='../templates/supervisor/supervisor_log.pt')
    def view(self):
        import xmlrpclib
        # TODO: dont use hardcoded urls
        self.server = xmlrpclib.Server('http://localhost:9001/RPC2')
        name = self.request.matchdict.get('name')
        
        log = self.server.supervisor.tailProcessStdoutLog(name, 0, 4096)
        log_list = log[0].split('\n')
        return dict(name=name, log=log_list)

