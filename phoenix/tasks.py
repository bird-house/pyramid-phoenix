from pyramid_celery import celery_app as app

from owslib.wps import WebProcessingService, monitorExecution
import json
import yaml
import uuid
import urllib
from datetime import datetime

from phoenix.models import mongodb

from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)

def task_result(task_id):
    return app.AsyncResult(task_id)

def log(job):
    log_msg = '{0:3d}%: {1}'.format(job.get('progress'), job.get('status_message'))
    if not 'log' in job:
        job['log'] = []
    # skip same log messages
    if len(job['log']) == 0 or job['log'][-1] != log_msg:
        job['log'].append(log_msg)
        logger.info(log_msg)

def log_error(job, error):
    log_msg = 'ERROR: {0.text} - code={0.code} - locator={0.locator}'.format(error)
    if not 'log' in job:
        job['log'] = []
    # skip same log messages
    if len(job['log']) == 0 or job['log'][-1] != log_msg:
        job['log'].append(log_msg)
        logger.error(log_msg)

def add_job(db, user_id, task_id, title, abstract, status_location, is_workflow=False):
    job = dict(
        identifier = str(uuid.uuid1()),
        task_id = task_id,
        email = user_id,
        is_workflow = is_workflow,
        title = title,
        abstract = abstract,
        status_location = status_location,
        created = datetime.now(),
        is_complete = False)
    db.jobs.save(job)
    return job

@app.task(bind=True)
def esgf_logon(self, email, url, openid, password):
    registry = app.conf['PYRAMID_REGISTRY']
    inputs = []
    inputs.append( ('openid', openid.encode('ascii', 'ignore')) )
    inputs.append( ('password', password.encode('ascii', 'ignore')) )
    outputs = [('output',True),('expires',False)]

    wps = WebProcessingService(url=url, skip_caps=True)
    execution = wps.execute(identifier="esgf_logon", inputs=inputs, output=outputs)
    monitorExecution(execution)
    
    if execution.isSucceded():
        credentials = execution.processOutputs[0].reference
        cert_expires = execution.processOutputs[1].data[0]
        db = mongodb(registry)
        user = db.users.find_one({'email':email})
        user['credentials'] = credentials
        user['cert_expires'] = cert_expires
        db.users.update({'email':email}, user)
    return execution.status

@app.task(bind=True)
def execute_workflow(self, user_id, url, workflow):
    registry = app.conf['PYRAMID_REGISTRY']

    # generate and run dispel workflow
    # TODO: fix owslib wps for unicode/yaml parameters
    inputs=[('workflow', json.dumps(workflow))]
    outputs=[('output', True)]
    
    wps = WebProcessingService(url=url, skip_caps=True)
    execution = wps.execute(identifier='workflow', inputs=inputs, output=outputs)
    db = mongodb(registry)
    job = add_job(db, user_id,
                  task_id = self.request.id,
                  is_workflow = True,
                  title = workflow['worker']['identifier'],
                  abstract = '',
                  status_location = execution.statusLocation)

    while not execution.isComplete():
        execution.checkStatus(sleepSecs=1)
        job['status'] = execution.getStatus()
        job['status_message'] = execution.statusMessage
        job['is_complete'] = execution.isComplete()
        job['is_succeded'] = execution.isSucceded()
        job['progress'] = execution.percentCompleted
        duration = datetime.now() - job.get('created', datetime.now())
        job['duration'] = str(duration).split('.')[0]
        if execution.isComplete():
            job['finished'] = datetime.now()
            if execution.isSucceded():
                result_url = execution.processOutputs[0].reference
                result = json.load(urllib.urlopen(result_url))
                job['worker_status_location'] = result.get('worker', [''])[0]
                job['source_status_location'] = result.get('source', [''])[0]
                job['progress'] = 100
        log(job)
        for error in execution.errors:
            log_error(job, error)
        db.jobs.update({'identifier': job['identifier']}, job)
    return execution.getStatus()

@app.task(bind=True)
def execute_process(self, user_id, url, identifier, inputs, outputs, keywords=None):
    registry = app.conf['PYRAMID_REGISTRY']

    wps = WebProcessingService(url=url, skip_caps=True)
    execution = wps.execute(identifier, inputs=inputs, output=outputs)
    db = mongodb(registry)
    job = add_job(db, user_id,
                  task_id = self.request.id,
                  is_workflow = False,
                  title = execution.process.title,
                  abstract = getattr(execution.process, "abstract", ""),
                  status_location = execution.statusLocation)

    while not execution.isComplete():
        execution.checkStatus(sleepSecs=1)
        job['status'] = execution.getStatus()
        job['status_message'] = execution.statusMessage
        job['is_complete'] = execution.isComplete()
        job['is_succeded'] = execution.isSucceded()
        job['progress'] = execution.percentCompleted
        duration = datetime.now() - job.get('created', datetime.now())
        job['duration'] = str(duration).split('.')[0]
        if execution.isComplete():
            job['finished'] = datetime.now()
            if execution.isSucceded():
                job['progress'] = 100
        log(job)
        for error in execution.errors:
            log_error(job, error)
        db.jobs.update({'identifier': job['identifier']}, job)
    return execution.getStatus()
