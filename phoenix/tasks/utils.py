import datetime
import json

from phoenix.db import mongodb
from phoenix.twitcherclient import generate_access_token

from pyramid_celery import celery_app as app
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


def task_result(task_id):
    return app.AsyncResult(task_id)


def wait_secs(run_step=-1):
    secs_list = (2, 2, 2, 2, 2, 5, 5, 5, 5, 5, 10, 10, 10, 10, 10, 20, 20, 20, 20, 20, 30)
    if run_step >= len(secs_list):
        run_step = -1
    return secs_list[run_step]


def dump_json(obj):
    def date_handler(obj):
        if isinstance(obj, datetime.datetime) or isinstance(obj, datetime.date):
            date_formatted = obj.isoformat()
        else:
            date_formatted = None
        return date_formatted
    return json.dumps(obj, default=date_handler)


def save_log(job, error=None):
    if error:
        log_msg = 'ERROR: {0.text} - code={0.code} - locator={0.locator}'.format(error)
    else:
        log_msg = '{0} {1:3d}%: {2}'.format(
            job.get('duration', 0),
            job.get('progress', 0),
            job.get('status_message', 'no message'))
    if 'log' not in job:
        job['log'] = []
    # skip same log messages
    if len(job['log']) == 0 or job['log'][-1] != log_msg:
        job['log'].append(log_msg)
        if error:
            logger.error(log_msg)
        else:
            logger.info(log_msg)


def add_job(db, task_id, process_id, title=None, abstract=None,
            service_name=None, service=None, status_location=None,
            caption=None, userid=None,
            async=True):
    tags = ['dev']
    if async:
        tags.append('async')
    else:
        tags.append('sync')
    job = dict(
        identifier=task_id,
        task_id=task_id,             # TODO: why not using as identifier?
        userid=userid or 'guest',
        service_name=service_name,        # wps service name (service identifier)
        service=service or service_name,  # wps service title (url, service_name or service title)
        process_id=process_id,                  # process identifier
        title=title or process_id,              # process title (identifier or title)
        abstract=abstract or "No Summary",
        status_location=status_location,
        created=datetime.datetime.now(),
        tags=tags,
        caption=caption,
        status="ProcessAccepted",
        response=None,
        request=None,
    )
    db.jobs.insert(job)
    return job


def get_access_token(userid):
    registry = app.conf['PYRAMID_REGISTRY']
    # db = mongodb(registry)
    # refresh access token
    token = generate_access_token(registry, userid=userid)
    return token.get('access_token')


def wps_headers(userid):
    headers = {}
    if userid:
        access_token = get_access_token(userid)
        if access_token:
            headers['Access-Token'] = access_token
    return headers
