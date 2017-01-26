import requests

from pyramid.view import view_config
from pyramid.events import subscriber
from pyramid.response import Response

from phoenix.events import JobFinished, JobStarted

import logging
LOGGER = logging.getLogger(__name__)


@view_config(route_name='wpsoutputs')
def wpsoutputs(request):
    filename = request.matchdict.get('filename')
    url = request.registry.settings.get('wps.output.url')
    url += '/wpsoutputs'
    url += filename
    LOGGER.debug("delegate to wpsoutputs: %s", url)
    # forward request to target (without Host Header)
    # h = dict(request.headers)
    # h.pop("Host", h)
    response = requests.get(url, verify=False)
    response.raise_for_status()

    return Response(body=response.content, status=response.status_code, headers=response.headers)


@subscriber(JobStarted)
def notify_job_started(event):
    event.request.session.flash(
        '<h4><img src="/static/phoenix/img/ajax-loader.gif"></img> Job Created. Please wait ...</h4>', queue='warning')


@subscriber(JobFinished)
def notify_job_finished(event):
    if event.succeeded():
        LOGGER.info("job %s succeded.", event.job.get('title'))
        # event.request.session.flash("Job <b>{0}</b> succeded.".format(event.job.get('title')), queue='success')
    else:
        LOGGER.warn("job %s failed.", event.job.get('title'))
        # logger.warn("status = %s", event.job.get('status'))
        # event.request.session.flash("Job <b>{0}</b> failed.".format(event.job.get('title')), queue='danger')
