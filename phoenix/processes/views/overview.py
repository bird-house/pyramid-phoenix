from pyramid.view import view_config, view_defaults

from phoenix.catalog import WPS_TYPE
from phoenix.views import MyView

import logging
LOGGER = logging.getLogger(__name__)


@view_defaults(permission='view', layout="default")
class Overview(MyView):
    def __init__(self, request):
        super(Overview, self).__init__(request, name='processes', title='')

    @view_config(route_name='processes', renderer='../templates/processes/overview.pt', accept='text/html')
    def view(self):
        items = []
        for service in self.request.catalog.get_services(service_type=WPS_TYPE):
            # TODO: get name from service object
            service_name = self.request.catalog.get_service_name(service)
            LOGGER.debug('got wps service name: %s', service_name)
            url = self.request.route_path('processes_list', _query=[('wps', service_name)])
            items.append(dict(title=service.title, description=service.abstract, public=service.public, url=url))
        processes = []
        url = self.request.route_path('processes_execute', _query=[('wps', 'hummingbird'), ('process', 'spotchecker')])
        processes.append(dict(title='spotchecker', description='Spot Checker checks ...', url=url))
        url = self.request.route_path('processes_execute', _query=[('wps', 'hummingbird'), ('process', 'ncdump')])
        processes.append(dict(title='ncdump', description='NCDump dumps ...', url=url))
        return dict(title="Web Processing Services", items=items, processes=processes)
