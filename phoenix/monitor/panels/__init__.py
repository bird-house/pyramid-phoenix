from pyramid_layout.panel import panel_config

from phoenix.utils import time_ago_in_words

import logging
logger = logging.getLogger(__name__)

def job_details(request, job_id):
    job = request.db.jobs.find_one({'identifier': job_id})
    details = {}
    if job is not None:
        details['identifier'] = job.get('identifier')
        details['title'] = job.get('title')
        details['abstract'] = job.get('abstract')
        details['status'] = job.get('status', 'unknown')
        details['finished'] = time_ago_in_words(job.get('finished'))
        details['progress'] = job.get('progress')
        details['duration'] = job.get('duration')
        details['status_message'] = job.get('status_message')
        details['status_location'] = job.get('status_location')
        details['caption'] = job.get('caption', '???')
        details['tags'] = job.get('tags')
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
