from pyramid.view import view_config, view_defaults

from owslib.wps import WebProcessingService

from phoenix.catalog import WPS_TYPE

import logging
LOGGER = logging.getLogger(__name__)


def includeme(config):
    config.add_route('process_list', 'processes/list.json')


@view_defaults(permission='admin')
class ProcessesActions(object):
    """Actions related to processe."""

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.session = self.request.session

    @view_config(route_name='process_list', renderer='json')
    def list_processes(self):
        processes = {}
        for service in self.request.catalog.get_services(service_type=WPS_TYPE):
            service_name = self.request.catalog.get_service_name(service)
            wps = WebProcessingService(
                url=self.request.route_url('owsproxy', service_name=service_name),
                verify=False)
            processes[service_name] = [process.identifier for process in wps.processes]
        return processes
