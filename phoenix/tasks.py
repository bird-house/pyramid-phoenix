from pyramid_celery import celery_app as app

from owslib.wps import WebProcessingService, monitorExecution
import json
import uuid
import urllib
from datetime import datetime

from phoenix.models import mongodb

def task_result(task_id):
    return app.AsyncResult(task_id)

@app.task
def esgf_logon(email, url, openid, password):
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

@app.task
def execute_workflow(email, url, name, nodes):
    registry = app.conf['PYRAMID_REGISTRY']

    nodes_json = json.dumps(nodes)
    # generate and run dispel workflow
    identifier='dispel'
    inputs=[('nodes', nodes_json), ('name', name)]
    outputs=[('output', True)]
    
    wps = WebProcessingService(url=url, skip_caps=True)
    execution = wps.execute(identifier, inputs=inputs, output=outputs)
    db = mongodb(registry)
    
    log = ['0%: process started']

    job = dict(
        identifier = uuid.uuid4().get_hex(),
        email = email,
        title = nodes['worker']['identifier'],
        abstract = '',
        workflow_status_location = execution.statusLocation,
        created = datetime.now(),
        is_complete = False,
        log = log)
    db.jobs.save(job)

    while not execution.isComplete():
        execution.checkStatus(sleepSecs=2)
        job['status'] = execution.getStatus()
        job['status_message'] = execution.statusMessage
        job['is_complete'] = execution.isComplete()
        job['is_succeded'] = execution.isSucceded()
        job['progress'] = execution.percentCompleted
        job['errors'] = [ '%s %s\n: %s' % (error.code, error.locator, error.text.replace('\\','')) for error in execution.errors]
        duration = datetime.now() - job.get('created', datetime.now())
        job['duration'] = str(duration).split('.')[0]
        log.append('%d: %s' % (execution.percentCompleted, execution.statusMessage))
        if execution.isComplete():
            job['finished'] = datetime.now()
            result_url = execution.processOutputs[0].reference
            result = json.load(urllib.urlopen(result_url))
            job['status_location'] = result.get('worker', [''])[0]
            job['resource_status_location'] = result.get('source', [''])[0]
        if execution.isSucceded():
            job['progress'] = 100
        job['log'] = log
        db.jobs.update({'identifier': job['identifier']}, job)
    return execution.getStatus()

@app.task
def execute_process(email, url, identifier, inputs, outputs, keywords=None):
    registry = app.conf['PYRAMID_REGISTRY']

    wps = WebProcessingService(url=url, skip_caps=True)
    execution = wps.execute(identifier, inputs=inputs, output=outputs)
    db = mongodb(registry)

    log = ['0%: process started']

    job = dict(
        identifier = uuid.uuid4().get_hex(),
        email = email,
        title = execution.process.title,
        abstract = getattr(execution.process, "abstract", ""),
        status_location = execution.statusLocation,
        created = datetime.now(),
        is_complete = False,
        log = log)
    db.jobs.save(job)

    while not execution.isComplete():
        execution.checkStatus(sleepSecs=2)
        job['status'] = execution.getStatus()
        job['status_message'] = execution.statusMessage
        job['is_complete'] = execution.isComplete()
        job['is_succeded'] = execution.isSucceded()
        log.append('%d: %s' % (execution.percentCompleted, execution.statusMessage))
        job['errors'] = [ '%s %s\n: %s' % (error.code, error.locator, error.text.replace('\\','')) for error in execution.errors]
        duration = datetime.now() - job.get('created', datetime.now())
        job['duration'] = str(duration).split('.')[0]
        if execution.isComplete():
            job['finished'] = datetime.now()
        if execution.isSucceded():
            job['progress'] = 100
        else:
            job['progress'] = execution.percentCompleted
        job['log'] = log
        db.jobs.update({'identifier': job['identifier']}, job)
    return execution.getStatus()
