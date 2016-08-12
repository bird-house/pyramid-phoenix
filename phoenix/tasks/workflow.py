from datetime import datetime
import yaml
import json
import urllib

from pyramid_celery import celery_app as app

from owslib.wps import WebProcessingService, ComplexDataInput
from owslib.util import build_get_url

from phoenix.db import mongodb
from phoenix.events import JobFinished
from phoenix.tasks import wps_headers, log, log_error, add_job

from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)


@app.task(bind=True)
def execute_workflow(self, userid, url, workflow, caption=None):
    registry = app.conf['PYRAMID_REGISTRY']
    db = mongodb(registry)

    # generate and run dispel workflow
    # TODO: fix owslib wps for unicode/yaml parameters
    logger.debug('workflow=%s', workflow)
    headers = wps_headers(userid)
    # TODO: handle access token in workflow
    workflow['worker']['url'] = build_get_url(workflow['worker']['url'],
                                              {'access_token': headers.get('Access-Token', '')})
    logger.debug('workflow_mod=%s', workflow)
    inputs = [('workflow', ComplexDataInput(json.dumps(workflow), mimeType="text/yaml", encoding="UTF-8"))]
    logger.debug('inputs=%s', inputs)
    outputs = [('output', True), ('logfile', True)]

    wps = WebProcessingService(url=url, skip_caps=True, verify=False, headers=headers)
    worker_wps = WebProcessingService(url=workflow['worker']['url'], skip_caps=False, verify=False)
    execution = wps.execute(identifier='workflow', inputs=inputs, output=outputs, lineage=True)

    job = add_job(db, userid,
                  task_id=self.request.id,
                  is_workflow=True,
                  service=worker_wps.identification.title,
                  title=workflow['worker']['identifier'],
                  abstract='',
                  caption=caption,
                  status_location=execution.statusLocation)

    while execution.isNotComplete():
        try:
            execution.checkStatus(sleepSecs=3)
            job['status'] = execution.getStatus()
            job['status_message'] = execution.statusMessage
            job['progress'] = execution.percentCompleted
            duration = datetime.now() - job.get('created', datetime.now())
            job['duration'] = str(duration).split('.')[0]
            if execution.isComplete():
                job['finished'] = datetime.now()
                if execution.isSucceded():
                    for output in execution.processOutputs:
                        if 'output' == output.identifier:
                            result = yaml.load(urllib.urlopen(output.reference))
                            job['worker_status_location'] = result['worker']['status_location']
                    job['progress'] = 100
                    log(job)
                else:
                    job['status_message'] = '\n'.join(error.text for error in execution.errors)
                    for error in execution.errors:
                        log_error(job, error)
            else:
                log(job)
        except:
            logger.exception("Could not read status xml document.")
        else:
            db.jobs.update({'identifier': job['identifier']}, job)
    registry.notify(JobFinished(job))
    return execution.getStatus()

