from datetime import datetime

from pyramid_celery import celery_app as app

from owslib.wps import WebProcessingService

from phoenix.db import mongodb
from phoenix.events import JobFinished
from phoenix.tasks.utils import wps_headers, log, log_error, add_job, wait_secs

from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)


@app.task(bind=True)
def execute_process(self, url, identifier, inputs, outputs, async=True, userid=None, caption=None):
    registry = app.conf['PYRAMID_REGISTRY']
    db = mongodb(registry)
    job = add_job(
        db,
        userid=userid,
        task_id=self.request.id,
        service=url,
        process_id=identifier,
        is_workflow=False,
        caption=caption)

    try:
        wps = WebProcessingService(url=url, skip_caps=False, verify=False, headers=wps_headers(userid))
        execution = wps.execute(identifier, inputs=inputs, output=outputs, async=async, lineage=True)
        job['service'] = wps.identification.title
        # job['title'] = getattr(execution.process, "title")
        job['abstract'] = getattr(execution.process, "abstract")
        job['status_location'] = execution.statusLocation

        logger.debug("job init done %s ...", self.request.id)

        num_retries = 0
        run_step = 0
        while execution.isNotComplete() or not run_step:
            if num_retries >= 5:
                raise Exception("Could not read status document after 5 retries. Giving up.")
            try:
                execution.checkStatus(sleepSecs=wait_secs(run_step))
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
                num_retries += 1
                logger.exception("Could not read status xml document for job %s. Trying again ...", self.request.id)
            else:
                logger.debug("update job %s ...", self.request.id)
                num_retries = 0
                run_step += 1
                db.jobs.update({'identifier': job['identifier']}, job)
    except Exception as exc:
        logger.exception("Failed to run Job")
        job['status'] = "ProcessFailed"
        job['status_message'] = "Failed to run Job. %s" % exc.message
    finally:
        log(job)
        db.jobs.update({'identifier': job['identifier']}, job)

    registry.notify(JobFinished(job))
    return job['status']
