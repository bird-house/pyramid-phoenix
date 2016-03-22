import logging
logger = logging.getLogger(__name__)

def includeme(config):
    settings = config.registry.settings

    logger.info('Add monitor')

    config.add_route('monitor', '/monitor')
    config.add_route('remove_job', '/monitor/{job_id}/remove')
    config.add_route('remove_all_jobs', '/monitor/remove_all')
    config.add_route('update_myjobs', '/monitor/update.json')
    config.add_route('monitor_details', '/monitor/{job_id}/{tab}')

    
