import logging
LOGGER = logging.getLogger(__name__)


def includeme(config):
    # views
    config.add_route('monitor', '/monitor')
    config.add_route('job_details', '/monitor/details/{job_id}/{tab}')
