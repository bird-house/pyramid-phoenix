from pyramid.view import view_config, view_defaults

from pyramid.httpexceptions import HTTPException, HTTPFound, HTTPNotFound
from deform import Form, Button
from deform import ValidationFailure

from phoenix.view import MyView

import logging
logger = logging.getLogger(__name__)

@view_defaults(permission='edit', layout='default')
class MyJobs(MyView):
    def __init__(self, request):
        super(MyJobs, self).__init__(request, 'My Jobs')
        self.db = self.request.db 

    def sort_order(self):
        """Determine what the current sort parameters are.
        """
        order = self.request.GET.get('order_col', 'creation_time')
        order_dir = self.request.GET.get('order_dir', 'desc')
        order_dir = 1 if order_dir == 'asc' else -1
        return dict(order=order, order_dir=order_dir)

    def update_job(self, job):
        from owslib.wps import WPSExecution
        
        try:
            execution = WPSExecution(url = job['wps_url'])
            execution.checkStatus(url = job['status_location'], sleepSecs=0)
            job['status'] = execution.getStatus()
            job['status_message'] = execution.statusMessage
            job['is_complete'] = execution.isComplete()
            job['is_succeded'] = execution.isSucceded() 
            if execution.isSucceded():
                job['progress'] = 100
                self.session.flash("Job %s completed." % job['title'], queue='success')
            else:
                job['progress'] = execution.percentCompleted
            # update db
            self.db.jobs.update({'identifier': job['identifier']}, job)
        except:
            logger.exception("could not update job %s", job.get('identifier'))
    
    @view_config(renderer='json', name='update.jobs')
    def update_jobs(self):
        logger.debug('!!!!! update job !!!!')
        jobs = list(self.db.jobs.find({'email': self.user_email(), 'is_complete':False}))
        for job in jobs:
            logger.debug('update job, %s', job.get('identifier'))
            self.update_job(job)
        return jobs

    @view_config(renderer='json', name='deleteall.job')
    def delete_all(self):
        self.db.jobs.remove({'email': self.user_email()})
        return {}

    @view_config(renderer='json', name='delete.job')
    def delete(self):
        jobid = self.request.params.get('jobid', None)
        if jobid is not None:
            self.db.jobs.remove({'identifier': jobid})
        return {}
    
    @view_config(route_name='myjobs', renderer='phoenix:templates/myjobs.pt')
    def view(self):
        order = self.sort_order()
        key=order.get('order')
        direction=order.get('order_dir')

        self.update_jobs()
        items = list(self.db.jobs.find({'email': self.user_email()}).sort(key, direction))
        
        from phoenix.grid import JobsGrid
        grid = JobsGrid(
                self.request,
                items,
                ['status', 'creation_time', 'title', 'status_message', 'status_location', 'progress', 'action'],
            )
        return dict(grid=grid, items=items)
