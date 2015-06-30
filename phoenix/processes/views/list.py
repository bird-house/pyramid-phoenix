from pyramid.view import view_config, view_defaults

from owslib.wps import WebProcessingService

from phoenix.processes.views import Processes
from phoenix.catalog import wps_url, wps_caps_url

import logging
logger = logging.getLogger(__name__)

class ProcessList(Processes):
    def __init__(self, request):
        self.wps_id = request.params.get('wps')
        self.wps = WebProcessingService(url=wps_url(request, self.wps_id))
        super(ProcessList, self).__init__(request, name='processes_list', title='')
        
    def breadcrumbs(self):
        breadcrumbs = super(ProcessList, self).breadcrumbs()
        breadcrumbs.append(dict(route_path=self.request.route_path(self.name), title=self.wps.identification.title))
        return breadcrumbs

    @view_config(route_name='processes_list', renderer='../templates/processes/list.pt')
    def view(self):
        items = []
        for process in self.wps.processes:
            item = {}
            item['title'] = "{0.title} {0.processVersion}".format(process)
            item['description'] = getattr(process, 'abstract', '')
            item['url'] = self.request.route_path('processes_execute', _query=[('wps', self.wps_id), ('process', process.identifier)])
            items.append(item)
        return dict(
            url=wps_caps_url(self.request, self.wps_id),
            description=self.wps.identification.abstract,
            provider_name=self.wps.provider.name,
            provider_site=self.wps.provider.url,
            items=items)

