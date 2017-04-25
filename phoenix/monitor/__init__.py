import logging
LOGGER = logging.getLogger(__name__)


def includeme(config):
    settings = config.registry.settings

    # views
    config.add_route('monitor', '/monitor')
    config.add_route('monitor_details', '/monitor/details/{job_id}/{tab}')
    config.add_route('job_status', '/monitor/status/{job_id}')
    # actions
    config.include('phoenix.monitor.views.actions')
