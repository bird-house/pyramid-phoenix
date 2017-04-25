from pyramid.view import view_config, view_defaults

from owslib.wps import WebProcessingService

from phoenix.catalog import WPS_TYPE

import logging
LOGGER = logging.getLogger(__name__)


def includeme(config):
    config.add_route('list_processes', 'processes/list.json')
    config.add_route('check_job', '/processes/check_job.json')


class ProcessesActions(object):
    """Actions related to processes."""

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.session = self.request.session

    @view_config(route_name='list_processes', renderer='json', permission='admin')
    def list_processes(self):
        processes = {}
        for service in self.request.catalog.get_services(service_type=WPS_TYPE):
            service_name = self.request.catalog.get_service_name(service)
            wps = WebProcessingService(
                url=self.request.route_url('owsproxy', service_name=service_name),
                verify=False)
            processes[service_name] = [process.identifier for process in wps.processes]
        return processes

    @view_config(route_name='check_job', renderer='json', permission='view')
    def check_job(self):
        status = 'running'
        task_id = self.session.get('task_id')
        collection = self.request.db.jobs
        if collection.find({"task_id": task_id}).count() == 1:
            status = 'ready'
        return dict(status=status)
