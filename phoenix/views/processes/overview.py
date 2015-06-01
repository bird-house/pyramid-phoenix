from pyramid.view import view_config, view_defaults

from phoenix.views.processes import Processes
from phoenix.grid import MyGrid
from phoenix import models

import logging
logger = logging.getLogger(__name__)

class Overview(Processes):
    def __init__(self, request):
        super(Processes, self).__init__(request, name='processes', title='')

    def breadcrumbs(self):
        breadcrumbs = super(Overview, self).breadcrumbs()
        return breadcrumbs

    @view_config(route_name='processes', renderer='phoenix:templates/processes/overview.pt')
    def view(self):
        items = models.get_wps_list(self.request)

        grid = OverviewGrid(
                self.request,
                items,
                ['Web Processing Service', ''],
            )
        return dict(grid=grid)

class OverviewGrid(MyGrid):
    def __init__(self, request, *args, **kwargs):
        super(OverviewGrid, self).__init__(request, *args, **kwargs)
        self.labels['Web Processing Service'] = ''
        self.column_formats['Web Processing Service'] = self.title_td
        self.column_formats[''] = self.action_td
        self.exclude_ordering = self.columns

    def title_td(self, col_num, i, item):
        return self.render_title_td(
            title=item.get('title'), 
            abstract=item.get('abstract'),
            format='XML',
            source=item.get('source'))

    def action_td(self, col_num, i, item):
        route_path = self.request.route_path('processes_list', _query=[('url', item.get('source'))])
        logger.debug('route path = %s', route_path)
        
        buttongroup = []
        buttongroup.append( ("submit", "", "glyphicon glyphicon-play", "Show Processes", 
                             route_path, False) )
        return self.render_action_td(buttongroup)
    