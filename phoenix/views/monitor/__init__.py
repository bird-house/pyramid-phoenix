from pyramid.view import view_config, view_defaults
from pyramid.events import subscriber

from phoenix.views import MyView
from phoenix.events import JobFinished

import logging
logger = logging.getLogger(__name__)

@subscriber(JobFinished)
def notify_job_finished(event):
    if event.success:
        logger.info("job %s succeded.", event.job.get('title'))
        #event.request.session.flash("Job <b>%s</b> succeded." % event.job.get('title'), queue='success')
    else:
        logger.warn("job %s failed.", event.job.get('title'))
        #self.session.flash("Job <b>%s</b> failed." % event.job.get('title'), queue='danger')

@view_defaults(permission='submit', layout='default')
class Monitor(MyView):
    def __init__(self, request, name, title, description=None):
        super(Monitor, self).__init__(request, name, title, description)
        
    def breadcrumbs(self):
        breadcrumbs = super(Monitor, self).breadcrumbs()
        breadcrumbs.append(dict(route_path=self.request.route_path('monitor'), title='Monitor'))
        return breadcrumbs

   
