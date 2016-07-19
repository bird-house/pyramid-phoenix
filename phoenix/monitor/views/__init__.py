from pyramid.view import view_config, view_defaults
from pyramid.events import subscriber
from pyramid.httpexceptions import HTTPFound
from pyramid.security import authenticated_userid

from phoenix.views import MyView
from phoenix.events import JobFinished, JobStarted

import logging
logger = logging.getLogger(__name__)

@subscriber(JobStarted)
def notify_job_started(event):
    event.request.session.flash("Job added to task queue. Please wait ...", queue='info')
    
@subscriber(JobFinished)
def notify_job_finished(event):
    if event.succeeded():
        logger.info("job %s succeded.", event.job.get('title'))
        #event.request.session.flash("Job <b>{0}</b> succeded.".format(event.job.get('title')), queue='success')
    else:
        logger.warn("job %s failed.", event.job.get('title'))
        #logger.warn("status = %s", event.job.get('status'))
        #event.request.session.flash("Job <b>{0}</b> failed.".format(event.job.get('title')), queue='danger')

@view_defaults(permission='view', layout='default')
class Monitor(MyView):
    def __init__(self, request, name, title, description=None):
        super(Monitor, self).__init__(request, name, title, description)
        
    def breadcrumbs(self):
        breadcrumbs = super(Monitor, self).breadcrumbs()
        breadcrumbs.append(dict(route_path=self.request.route_path('monitor'), title='Monitor'))
        return breadcrumbs

   
