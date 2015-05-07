from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPException, HTTPFound, HTTPNotFound

from phoenix.views.myjobs import MyJobs

from datetime import datetime

import logging
logger = logging.getLogger(__name__)

@view_defaults(permission='edit', layout='default')
class Overview(MyJobs):
    def __init__(self, request):
        super(Overview, self).__init__(request, name='myjobs_overview', title='Overview')
        self.db = self.request.db 

    def update_job(self, job):
        from owslib.wps import WPSExecution
        
        try:
            execution = WPSExecution(url = job['wps_url'])
            execution.checkStatus(url = job['status_location'], sleepSecs=0)
            job['status'] = execution.getStatus()
            job['status_message'] = execution.statusMessage
            job['is_complete'] = execution.isComplete()
            job['is_succeded'] = execution.isSucceded()
            job['errors'] = [ '%s %s\n: %s' % (error.code, error.locator, error.text.replace('\\','')) for error in execution.errors]
            duration = datetime.now() - job.get('created', datetime.now())
            job['duration'] = str(duration).split('.')[0]
            if execution.isComplete():
                job['finished'] = datetime.now()
            if execution.isSucceded():
                job['progress'] = 100
                self.session.flash("Job %s completed." % job['title'], queue='success')
            else:
                job['progress'] = execution.percentCompleted
            # update db
            self.db.jobs.update({'identifier': job['identifier']}, job)
        except:
            logger.exception("could not update job %s", job.get('identifier'))
    
    @view_config(renderer='json', route_name='update_myjobs')
    def update_jobs(self):
        jobs = list(self.db.jobs.find({'email': self.user_email(), 'is_complete':False}))
        for job in jobs:
            self.update_job(job)
        return jobs

    @view_config(route_name='remove_myjobs')
    def remove_all(self):
        count = self.db.jobs.find({'email': self.user_email()}).count()
        self.db.jobs.remove({'email': self.user_email()})
        self.session.flash("%d Jobs deleted." % count, queue='info')
        return HTTPFound(location=self.request.route_path('myjobs_overview'))

    @view_config(route_name='remove_myjob')
    def remove(self):
        jobid = self.request.matchdict.get('jobid')
        if jobid is not None:
            job = self.db.jobs.find_one({'identifier': jobid})
            self.db.jobs.remove({'identifier': jobid})
            self.session.flash("Job %s deleted." % job['title'], queue='info')
        return HTTPFound(location=self.request.route_path('myjobs_overview'))

    @view_config(route_name='myjobs_overview', renderer='phoenix:templates/myjobs/overview.pt')
    def view(self):
        self.update_jobs()
        items = list(self.db.jobs.find({'email': self.user_email()}).sort('created', -1))

        from phoenix.grid.jobs import JobsGrid
        grid = JobsGrid(
                self.request,
                items,
                ['status', 'job', 'duration', 'finished', 'progress', ''],
            )
        return dict(grid=grid, items=items)



