from pyramid.view import view_config, view_defaults

from phoenix.catalog import WPS_TYPE
from phoenix.catalog import get_service_name
from phoenix.processes.views import Processes

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
        for wps in self.request.catalog.get_services(service_type=WPS_TYPE):
            service_name = get_service_name(self.request, url=wps.source, name=wps.title)
            url=self.request.route_path('processes_list', _query=[('wps', service_name)])
            public = hasattr(wps, 'public') and wps.public
            items.append(dict(title=wps.title, description=wps.abstract, public=public, url=url))
        return dict(title="Web Processing Services", items=items)

    
