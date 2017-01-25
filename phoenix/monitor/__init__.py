import logging
logger = logging.getLogger(__name__)


def includeme(config):
    settings = config.registry.settings

    # logger.debug('Adding monitor ...')

    # internal wps outputs
    config.add_route('wpsoutputs', '/wpsoutputs*filename')

    # views
    config.add_route('monitor', '/monitor')
    config.add_route('monitor_details', '/monitor/details/{job_id}/{tab}')

    config.include('phoenix.monitor.views.actions')
