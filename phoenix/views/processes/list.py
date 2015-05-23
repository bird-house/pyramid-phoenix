from pyramid.view import view_config, view_defaults

from owslib.wps import WebProcessingService

from phoenix.views.processes import Processes

import logging
logger = logging.getLogger(__name__)

class ProcessList(Processes):
    def __init__(self, request):
        url=request.params.get('url', request.session.get('wps_url'))
        request.session['wps_url'] = url
        self.wps = WebProcessingService(url)
        super(ProcessList, self).__init__(request, name='processes_list', title='')
        
    def breadcrumbs(self):
        breadcrumbs = super(ProcessList, self).breadcrumbs()
        breadcrumbs.append(dict(route_path=self.request.route_path(self.name), title=self.wps.identification.title))
        return breadcrumbs

    @view_config(route_name='processes_list', renderer='phoenix:templates/processes/list.pt')
    def view(self):
        items = []
        for process in self.wps.processes:
            item = {}
            item['title'] = "{0.title} {0.processVersion}".format(process)
            item['description'] = getattr(process, 'abstract', '')
            item['url'] = self.request.route_path('processes_execute', _query=[('identifier', process.identifier)])
            items.append(item)
        return dict(
            url=self.wps.url,
            description=self.wps.identification.abstract,
            provider_name=self.wps.provider.name,
            provider_site=self.wps.provider.url,
            items=items)

