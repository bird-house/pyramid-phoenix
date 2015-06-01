from pyramid_layout.panel import panel_config

import logging
logger = logging.getLogger(__name__)

def job_details(request, jobid):
    job = request.db.jobs.find_one({'identifier': jobid})
    details = job.copy()
    from phoenix.utils import time_ago_in_words
    details['finished'] = time_ago_in_words(job.get('finished'))
    return details

@panel_config(name='monitor_details', renderer='../templates/panels/monitor_details.pt')
def details(context, request):
    jobid = request.session.get('jobid')
    return dict(job=job_details(request, jobid=jobid))

@panel_config(name='monitor_log', renderer='../templates/panels/monitor_log.pt')
def log(context, request):
    jobid = request.session.get('jobid')
    job = request.db.jobs.find_one({'identifier': jobid})
    logger.debug("log: %s", job.get('log'))
    return dict(log=job.get('log'))
