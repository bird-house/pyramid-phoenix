import uuid
from datetime import datetime

from pyramid_celery import celery_app as app

from phoenix.db import mongodb
from phoenix.security import generate_access_token

from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)


def task_result(task_id):
    return app.AsyncResult(task_id)


def log(job):
    log_msg = '{0:3d}%: {1}'.format(job.get('progress'), job.get('status_message'))
    if 'log' not in job:
        job['log'] = []
    # skip same log messages
    if len(job['log']) == 0 or job['log'][-1] != log_msg:
        job['log'].append(log_msg)
        logger.info(log_msg)


def log_error(job, error):
    log_msg = 'ERROR: {0.text} - code={0.code} - locator={0.locator}'.format(error)
    if 'log' not in job:
        job['log'] = []
    # skip same log messages
    if len(job['log']) == 0 or job['log'][-1] != log_msg:
        job['log'].append(log_msg)
        logger.error(log_msg)


def add_job(db, userid, task_id, service, title, abstract, status_location, is_workflow=False, caption=None):
    tags = ['dev']
    if is_workflow:
        tags.append('workflow')
    else:
        tags.append('single')
    job = dict(
        identifier=uuid.uuid4().get_hex(),
        task_id=task_id,
        userid=userid,
        is_workflow=is_workflow,
        service=service,
        title=title,
        abstract=abstract,
        status_location=status_location,
        created=datetime.now(),
        tags=tags,
        caption=caption,
        status="ProcessAccepted",
        )
    db.jobs.insert(job)
    return job


def get_access_token(userid):
    registry = app.conf['PYRAMID_REGISTRY']
    db = mongodb(registry)

    # update access token
    generate_access_token(registry, userid)
    
    user = db.users.find_one(dict(identifier=userid))
    return user.get('twitcher_token')


def wps_headers(userid):
    headers = {}
    if userid:
        access_token = get_access_token(userid)
        if access_token is not None:
            headers['Access-Token'] = access_token
    return headers






