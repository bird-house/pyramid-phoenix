from pyramid.view import view_config, view_defaults

from owslib.wps import WebProcessingService

from phoenix.views import MyView
from phoenix.utils import wps_caps_url

import logging
logger = logging.getLogger(__name__)


@view_defaults(permission='view', layout="default")
class ProcessList(MyView):
    def __init__(self, request):
        self.service_name = request.params.get('wps')
        self.wps = WebProcessingService(
            url=request.route_url('owsproxy', service_name=self.service_name),
            verify=False)
        super(ProcessList, self).__init__(request, name='processes_list', title='')
        
    def breadcrumbs(self):
        breadcrumbs = super(ProcessList, self).breadcrumbs()
        breadcrumbs.append(dict(route_path=self.request.route_path('processes'), title='Processes'))
        breadcrumbs.append(dict(route_path=self.request.route_path(self.name), title=self.wps.identification.title))
        return breadcrumbs

    @view_config(route_name='processes_list', renderer='../templates/processes/list.pt')
    def view(self):
        items = []
        for process in self.wps.processes:
            item = dict(
                title="{0.title} {0.processVersion}".format(process),
                description=getattr(process, 'abstract', ''),
                url=self.request.route_path('processes_execute',
                                            _query=[('wps', self.service_name), ('process', process.identifier)]))
            items.append(item)
        return dict(
            url=wps_caps_url(self.wps.url),
            description=self.wps.identification.abstract,
            provider_name=self.wps.provider.name,
            provider_site=self.wps.provider.url,
            items=items)

