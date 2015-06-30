from pyramid_layout.panel import panel_config

import logging
logger = logging.getLogger(__name__)

def job_details(request, job_id):
    job = request.db.jobs.find_one({'identifier': job_id})
    from phoenix.utils import time_ago_in_words
    details = {}
    details['identifier'] = job.get('identifier')
    details['title'] = job.get('title')
    details['abstract'] = job.get('abstract')
    details['status'] = job.get('status', 'unknown')
    details['finished'] = time_ago_in_words(job.get('finished'))
    details['progress'] = job.get('progress')
    details['duration'] = job.get('duration')
    details['status_message'] = job.get('progress')
    details['status_location'] = job.get('status_location')
    return details

@panel_config(name='monitor_details', renderer='../templates/panels/monitor_details.pt')
def details(context, request):
    job_id = request.session.get('job_id')
    return dict(job=job_details(request, job_id=job_id))

@panel_config(name='monitor_log', renderer='../templates/panels/monitor_log.pt')
def log(context, request):
    job_id = request.session.get('job_id')
    job = request.db.jobs.find_one({'identifier': job_id})
    return dict(log=job.get('log', []))
