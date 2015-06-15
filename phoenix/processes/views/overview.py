from pyramid.view import view_config, view_defaults

from phoenix.processes.views import Processes
from phoenix.catalog import get_wps_list

import logging
logger = logging.getLogger(__name__)

class Overview(Processes):
    def __init__(self, request):
        super(Processes, self).__init__(request, name='processes', title='')

    def breadcrumbs(self):
        breadcrumbs = super(Overview, self).breadcrumbs()
        return breadcrumbs

    @view_config(route_name='processes', renderer='../templates/processes/overview.pt')
    def view(self):
        items = []
        for wps in get_wps_list(self.request):
            url=self.request.route_path('processes_list', _query=[('wps', wps.identifier)])
            items.append(dict(title=wps.title, description=wps.abstract, url=url))
        return dict(title="Web Processing Services", items=items)

    
