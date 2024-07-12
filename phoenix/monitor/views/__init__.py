from pyramid.events import subscriber

from phoenix.events import JobFinished, JobStarted

import logging
LOGGER = logging.getLogger("PHOENIX")


@subscriber(JobFinished)
def notify_job_finished(event):
    if event.succeeded():
        LOGGER.info("job %s succeded.", event.job.get('title'))
        # event.request.session.flash("Job <b>{0}</b> succeded.".format(event.job.get('title')), queue='success')
    else:
        LOGGER.warn("job %s failed.", event.job.get('title'))
        # logger.warn("status = %s", event.job.get('status'))
        # event.request.session.flash("Job <b>{0}</b> failed.".format(event.job.get('title')), queue='danger')
