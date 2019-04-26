from datetime import datetime
from lxml import etree
from time import sleep

from pyramid_celery import celery_app as app

from owslib.wps import WebProcessingService
from owslib.wps import SYNC, ASYNC

from phoenix.db import mongodb
from phoenix.events import JobFinished
from phoenix.tasks.utils import wps_headers, save_log, add_job, wait_secs
from phoenix.wps import check_status

from celery.utils.log import get_task_logger
LOGGER = get_task_logger(__name__)


@app.task(bind=True)
def execute_process(self, url, service_name, identifier, inputs, outputs, async=True, userid=None, caption=None):
    registry = app.conf['PYRAMID_REGISTRY']
    db = mongodb(registry)
    job = add_job(
        db,
        userid=userid,
        task_id=self.request.id,
        service_name=service_name,
        process_id=identifier,
        async=async,
        caption=caption)

    try:
        wps = WebProcessingService(url=url, skip_caps=False, verify=False, headers=wps_headers(userid))
        # TODO: complex type detection is currently broken due to pywps bug.
        outputs = [('output', True)]
        try:
            # TODO: sync is non-default
            if async is False:
                mode = SYNC
            else:
                mode = ASYNC
            execution = wps.execute(
                identifier=identifier,
                inputs=inputs,
                output=outputs,
                mode=mode,
                lineage=True)
        except Exception:
            LOGGER.warn("Setting execution mode is not supported. Using default async mode.")
            execution = wps.execute(identifier,
                                    inputs=inputs,
                                    output=outputs
                                    )
        # job['service'] = wps.identification.title
        # job['title'] = getattr(execution.process, "title")
        job['abstract'] = getattr(execution.process, "abstract")
        job['status_location'] = execution.statusLocation
        job['request'] = execution.request
        job['response'] = etree.tostring(execution.response)

        LOGGER.debug("job init done %s ...", self.request.id)
        LOGGER.debug("status location={}".format(execution.statusLocation))

        num_retries = 0
        run_step = 0
        while execution.isNotComplete() or run_step == 0:
            if num_retries >= 5:
                raise Exception("Could not read status document after 5 retries. Giving up.")
            try:
                execution = check_status(url=execution.statusLocation, verify=False,
                                         sleep_secs=wait_secs(run_step))
                job['response'] = etree.tostring(execution.response)
                job['status'] = execution.getStatus()
                job['status_message'] = execution.statusMessage
                job['progress'] = execution.percentCompleted
                duration = datetime.now() - job.get('created', datetime.now())
                job['duration'] = str(duration).split('.')[0]

                if execution.isComplete():
                    job['finished'] = datetime.now()
                    if execution.isSucceded():
                        LOGGER.debug("job succeded")
                        job['progress'] = 100
                    else:
                        LOGGER.debug("job failed.")
                        job['status_message'] = '\n'.join(error.text for error in execution.errors)
                        for error in execution.errors:
                            save_log(job, error)
            except Exception:
                num_retries += 1
                LOGGER.exception("Could not read status xml document for job %s. Trying again ...", self.request.id)
                sleep(1)
            else:
                LOGGER.debug("update job %s ...", self.request.id)
                num_retries = 0
                run_step += 1
            finally:
                save_log(job)
                db.jobs.update({'identifier': job['identifier']}, job)
    except Exception as exc:
        LOGGER.exception("Failed to run Job")
        job['status'] = "ProcessFailed"
        job['status_message'] = "Error: {0}".format(exc.message)
    finally:
        save_log(job)
        db.jobs.update({'identifier': job['identifier']}, job)

    registry.notify(JobFinished(job))
    return job['status']
