import logging
logger = logging.getLogger(__name__)

def includeme(config):
    settings = config.registry.settings

    logger.info('Adding monitor ...')

    # views
    config.add_route('monitor', '/monitor')
    config.add_route('monitor_details', '/monitor/details/{job_id}/{tab}')

    # actions
    config.add_route('update_myjobs', '/monitor/update.json')

    config.include('phoenix.monitor.views.actions')

    
