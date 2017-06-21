from pyramid.view import view_config, view_defaults

from owslib.wps import WebProcessingService

from phoenix.catalog import WPS_TYPE


def includeme(config):
    config.add_route('list_processes', 'processes/list.json')


class ProcessesActions(object):
    """Actions related to processes."""

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.session = self.request.session

    @view_config(route_name='list_processes', renderer='json', permission='admin', require_csrf=True)
    def list_processes(self):
        processes = {}
        for service in self.request.catalog.get_services(service_type=WPS_TYPE):
            service_name = self.request.catalog.get_service_name(service)
            wps = WebProcessingService(
                url=self.request.route_url('owsproxy', service_name=service_name),
                verify=False)
            processes[service_name] = [process.identifier for process in wps.processes]
        return processes
