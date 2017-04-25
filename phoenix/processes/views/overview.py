from pyramid.view import view_config, view_defaults

from owslib.wps import WebProcessingService

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
        settings = self.request.db.settings.find_one() or {}
        processes = []
        for pinned in settings.get('pinned_processes'):
            service_name, identifier = pinned.split('.', 1)
            url = self.request.route_path('processes_execute', _query=[('wps', service_name), ('process', identifier)])
            wps = WebProcessingService(url=self.request.route_url('owsproxy', service_name=service_name), verify=False)
            # TODO: need to fix owslib to handle special identifiers
            process = wps.describeprocess(identifier)
            processes.append(dict(title=process.identifier, description=process.abstract[:100], url=url))
        return dict(title="Web Processing Services", items=items, processes=processes)
