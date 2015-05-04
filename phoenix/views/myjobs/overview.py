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
        
        grid = JobsGrid(
                self.request,
                items,
                ['status', 'job', 'duration', 'finished', 'progress', ''],
            )
        return dict(grid=grid, items=items)


from phoenix.grid import MyGrid

class JobsGrid(MyGrid):
    def __init__(self, request, *args, **kwargs):
        super(JobsGrid, self).__init__(request, *args, **kwargs)
        self.column_formats['status'] = self.status_td
        self.column_formats['job'] = self.job_td
        self.column_formats['duration'] = self.duration_td
        self.column_formats['finished'] = self.finished_td
        self.column_formats['progress'] = self.progress_td
        self.column_formats[''] = self.action_td
        self.exclude_ordering = self.columns

    def status_td(self, col_num, i, item):
        return self.render_status_td(item)
    
    def job_td(self, col_num, i, item):
        return self.render_label_td(item['title'])

    def duration_td(self, col_num, i, item):
        try:
            duration = item.get('finished', datetime.now()) - item.get('created')
            duration = str(duration).split('.')[0]
        except:
            duration = "???"
        finally:
            return self.render_label_td(duration)
        
    def finished_td(self, col_num, i, item):
        try:
            from webhelpers2.date import time_ago_in_words
            time_ago = time_ago_in_words(item.get('finished'), granularity='minute')
            time_ago = time_ago + " ago"
        except:
            time_ago = '???'
        finally:
            return self.render_label_td(time_ago)

    def progress_td(self, col_num, i, item):
        return self.render_progress_td(identifier=item.get('identifier'), progress = item.get('progress', 0))
        
    def action_td(self, col_num, i, item):
        buttongroup = []
        buttongroup.append( ("show", item.get('identifier'), "glyphicon glyphicon-eye-open", "", 
                             self.request.route_path('myjobs_details', tab='outputs', jobid=item.get('identifier')), False) )
        buttongroup.append( ("remove", item.get('identifier'), "glyphicon glyphicon-trash text-danger", "", 
                             self.request.route_path('remove_myjob', jobid=item.get('identifier')), False) )
        return self.render_action_td(buttongroup)

