from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from . import SettingsView

import logging
logger = logging.getLogger(__name__)

class Supervisor(SettingsView):
    def __init__(self, request):
        super(Supervisor, self).__init__(
            request, name='settings_supervisor', title='Supervisor')

    def breadcrumbs(self):
        breadcrumbs = super(Supervisor, self).breadcrumbs()
        breadcrumbs.append(dict(route_path=self.request.route_path(self.name), title=self.title))
        return breadcrumbs

    def get_all_process_info(self):
        import xmlrpclib
        server = xmlrpclib.Server('http://localhost:9001/RPC2')
        return server.supervisor.getAllProcessInfo()
        
    @view_config(route_name="settings_supervisor", renderer='../templates/settings/supervisor.pt')
    def view(self):
        grid = Grid(self.request, self.get_all_process_info(), ['title'])
        return dict(grid=grid)

from phoenix.grid import MyGrid
class Grid(MyGrid):
    def __init__(self, request, *args, **kwargs):
        super(Grid, self).__init__(request, *args, **kwargs)
        self.column_formats['title'] = self.title_td
        #self.column_formats[''] = self.action_td
        self.exclude_ordering = self.columns

    def title_td(self, col_num, i, item):
        return self.render_label_td(item.get('name'))

    ## def action_td(self, col_num, i, item):
    ##     buttongroup = []
    ##     buttongroup.append(
    ##         ("start", item.name, "glyphicon glyphicon-trash text-danger", "",
    ##         self.request.route_path('start_program', name=item.name),
    ##         False) )
    ##     return self.render_action_td(buttongroup)
       
