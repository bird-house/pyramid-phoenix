import logging
LOGGER = logging.getLogger(__name__)


def includeme(config):
    settings = config.registry.settings

    LOGGER.debug('Monitor enabled ...')

    # views
    config.add_route('monitor', '/monitor')
    config.add_route('monitor_details', '/monitor/details/{job_id}/{tab}')

    config.include('phoenix.monitor.views.actions')
