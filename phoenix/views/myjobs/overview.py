from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPException, HTTPFound, HTTPNotFound

from phoenix.views.myjobs import MyJobs

import logging
logger = logging.getLogger(__name__)

@view_defaults(permission='edit', layout='default')
class Overview(MyJobs):
    def __init__(self, request):
        super(Overview, self).__init__(request, name='myjobs_overview', title='Overview')
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
            job['errors'] = [ '%s %s\n: %s' % (error.code, error.locator, error.text.replace('\\','')) for error in execution.errors]
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
        return HTTPFound(location=self.request.route_url('myjobs'))

    @view_config(route_name='remove_myjob')
    def remove(self):
        jobid = self.request.matchdict.get('jobid')
        if jobid is not None:
            job = self.db.jobs.find_one({'identifier': jobid})
            self.db.jobs.remove({'identifier': jobid})
            self.session.flash("Job %s deleted." % job['title'], queue='info')
        return HTTPFound(location=self.request.route_url('myjobs'))

    @view_config(route_name='myjobs_overview', renderer='phoenix:templates/myjobs.pt')
    def view(self):
        order = self.sort_order()
        key=order.get('order')
        direction=order.get('order_dir')

        self.update_jobs()
        items = list(self.db.jobs.find({'email': self.user_email()}).sort(key, direction))
        
        grid = JobsGrid(
                self.request,
                items,
                ['title', 'status', 'creation_time', 'progress', ''],
            )
        return dict(grid=grid, items=items)


from string import Template
from webhelpers.html.builder import HTML
from phoenix.grid import MyGrid

class JobsGrid(MyGrid):
    def __init__(self, request, *args, **kwargs):
        super(JobsGrid, self).__init__(request, *args, **kwargs)
        #self.column_formats['workflow'] = self.workflow_td
        self.column_formats['creation_time'] = self.creation_time_td
        self.column_formats['status'] = self.status_td
        self.column_formats['title'] = self.title_td
        self.column_formats['progress'] = self.progress_td
        self.column_formats[''] = self.action_td

    def creation_time_td(self, col_num, i, item):
        return self.render_timestamp_td(item.get('creation_time'))

    def status_td(self, col_num, i, item):
        return self.render_status_td(item)

    def title_td(self, col_num, i, item):
        return self.render_title_td(item['title'], item['abstract'], item['keywords'].split(','))

    def progress_td(self, col_num, i, item):
        return self.render_progress_td(identifier=item.get('identifier'), progress = item.get('progress', 0))
        
    def action_td(self, col_num, i, item):
        buttongroup = []
        buttongroup.append( ("show", item.get('identifier'), "glyphicon glyphicon-th-list", "Show", 
                             self.request.route_url('process_outputs', tab='outputs', jobid=item.get('identifier')), False) )
        buttongroup.append( ("remove", item.get('identifier'), "glyphicon glyphicon-trash", "Remove", 
                             self.request.route_url('remove_myjob', jobid=item.get('identifier')), False) )
        return self.render_action_td(buttongroup)

