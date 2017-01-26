import logging
LOGGER = logging.getLogger(__name__)

from phoenix.monitor.views import wpsoutputs


def includeme(config):
    settings = config.registry.settings

    LOGGER.debug('Monitor enabled ...')

    # internal wps outputs
    config.add_route('wpsoutputs', '/wpsoutputs*subpath')
    config.add_view(wpsoutputs, route_name='wpsoutputs')

    # views
    config.add_route('monitor', '/monitor')
    config.add_route('monitor_details', '/monitor/details/{job_id}/{tab}')

    config.include('phoenix.monitor.views.actions')
