from pyramid.view import view_config, view_defaults

from phoenix.utils import wps_caps_url
from phoenix.processes.views.list import ProcessList


import logging
logger = logging.getLogger(__name__)

@view_defaults(permission='view', layout="default")
class ProcessListJson(ProcessList):
    def __init__(self, request):
        ProcessList.__init__(self, request)

    @view_config(route_name='processes_list', renderer='json', accept='application/json')
    def view(self):
        items = []
        for process in self.wps.processes:
            item = dict(
                identifier=process.identifier,
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

