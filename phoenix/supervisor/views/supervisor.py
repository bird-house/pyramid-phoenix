from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from phoenix.settings.views import SettingsView

import logging
logger = logging.getLogger(__name__)

class Supervisor(SettingsView):
    def __init__(self, request):
        super(Supervisor, self).__init__(request, name='supervisor', title='Supervisor')
        import xmlrpclib
        # TODO: dont use hardcoded url
        self.server = xmlrpclib.Server(self.settings.get('supervisor.url'))

    def breadcrumbs(self):
        breadcrumbs = super(Supervisor, self).breadcrumbs()
        breadcrumbs.append(dict(route_path=self.request.route_path(self.name), title=self.title))
        return breadcrumbs
   
    @view_config(route_name="supervisor_process")
    def supervisor_process(self):
        action = self.request.matchdict.get('action')
        name = self.request.matchdict.get('name')

        if action == 'start':
            self.server.supervisor.startProcess(name)
            self.session.flash("Service {0} started.".format(name), queue="success")
        elif action == 'stop':
            self.server.supervisor.stopProcess(name)
            self.session.flash("Service {0} stopped.".format(name), queue="danger")
        elif action == 'restart':
            self.server.supervisor.stopProcess(name)
            self.server.supervisor.startProcess(name)
            self.session.flash("Service {0} restarted.".format(name), queue="success")
        elif action == 'clear':
            self.server.supervisor.clearProcessLogs(name)
            self.session.flash("Logs of service {0} cleared.".format(name), queue="success")
        return HTTPFound(location=self.request.route_path(self.name))
        
    @view_config(route_name="supervisor", renderer='../templates/supervisor/supervisor.pt')
    def view(self):
        # TODO: show only wps processes
        grid = Grid(self.request, self.server.supervisor.getAllProcessInfo(), ['state', 'description', 'name', ''])
        return dict(grid=grid)

from phoenix.grid import CustomGrid

class Grid(CustomGrid):
    def __init__(self, request, *args, **kwargs):
        super(Grid, self).__init__(request, *args, **kwargs)
        self.column_formats['state'] = self.state_td
        self.column_formats[''] = self.buttongroup_td
        self.exclude_ordering = self.columns

    def state_td(self, col_num, i, item):
        return self.render_td(renderer="supervisor_state_td.mako", state=item.get('state'), statename=item.get('statename'))
        
    def buttongroup_td(self, col_num, i, item):
        from phoenix.utils import ActionButton
        buttons = []
        if item.get('state') == 20:
            buttons.append( ActionButton('restart', css_class="btn btn-success", icon="fa fa-refresh",
                                     href=self.request.route_path('supervisor_process', action='restart', name=item.get('name'))))
            buttons.append( ActionButton('stop', css_class="btn btn-danger", icon="fa fa-stop",
                                     href=self.request.route_path('supervisor_process', action='stop', name=item.get('name'))))
        else:
            buttons.append( ActionButton('start', icon="fa fa-play",
                                     href=self.request.route_path('supervisor_process', action='start', name=item.get('name'))))
        # TODO: enable clear button again
        buttons.append( ActionButton('tail', icon="fa fa-align-left",
                                     href=self.request.route_path('supervisor_log', name=item.get('name'), offset=0)))

        return self.render_buttongroup_td(buttons=buttons)


       
