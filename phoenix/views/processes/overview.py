from pyramid.view import view_config, view_defaults

from phoenix.views.processes import Processes
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
        wps_list = models.get_wps_list(self.request)
        items = []
        for wps in wps_list:
            url=self.request.route_path('processes_list', _query=[('url', wps.get('source'))])
            items.append(dict(title=wps.get('title'), description=wps.get('abstract'), url=url))
        return dict(title="Web Processing Services", items=items)

    
