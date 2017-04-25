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
        details['status_message'] = job.get('status_message', '')
        if len(details['status_message']) > 250:
            details['status_message'] = details['status_message'][:250] + " [..]"  # not more the 250 chars
        if job.get('status_location'):
            details['status_location'] = job['status_location']
        elif job.get('response'):
            details['response'] = job['response']
        details['caption'] = job.get('caption', '???')
        details['tags'] = job.get('tags')
    return details


@panel_config(name='job_details', renderer='../templates/monitor/panels/details.pt')
def details(context, request):
    job_id = request.matchdict.get('job_id')
    return dict(job=job_details(request, job_id=job_id))


@panel_config(name='job_log', renderer='../templates/monitor/panels/log.pt')
def log(context, request):
    job_id = request.matchdict.get('job_id')
    job = request.db.jobs.find_one({'identifier': job_id})
    return dict(log=job.get('log', []))


@panel_config(name='job_xml', renderer='../templates/monitor/panels/xml.pt')
def xml(context, request):
    job_id = request.matchdict.get('job_id')
    job = request.db.jobs.find_one({'identifier': job_id})
    return dict(xml=job.get('response'), job=job)
