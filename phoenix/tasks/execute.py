from datetime import datetime

from pyramid_celery import celery_app as app

from owslib.wps import WebProcessingService

from phoenix.db import mongodb
from phoenix.events import JobFinished
from phoenix.tasks.utils import wps_headers, log, log_error, add_job

from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)


@app.task(bind=True)
def execute_process(self, userid, url, identifier, inputs, outputs, caption=None):
    registry = app.conf['PYRAMID_REGISTRY']
    db = mongodb(registry)

    wps = WebProcessingService(url=url, skip_caps=False, verify=False, headers=wps_headers(userid))
    execution = wps.execute(identifier, inputs=inputs, output=outputs, lineage=True)

    if not userid:
        userid = 'guest'

    job = add_job(db, userid,
                  task_id=self.request.id,
                  is_workflow=False,
                  service=wps.identification.title,
                  title=identifier,
                  abstract=getattr(execution.process, "abstract", ""),
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