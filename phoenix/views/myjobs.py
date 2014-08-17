from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPException, HTTPFound, HTTPNotFound

from phoenix.views import MyView

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
        jobs = list(self.db.jobs.find({'email': self.user_email(), 'is_complete':False}))
        for job in jobs:
            self.update_job(job)
            
        return jobs

    @view_config(renderer='json', route_name='remove_myjobs')
    def remove_all(self):
        count = self.db.jobs.find({'email': self.user_email()}).count()
        self.db.jobs.remove({'email': self.user_email()})
        self.session.flash("%d Jobs deleted." % count, queue='info')
        return {}

    @view_config(renderer='json', route_name='remove_myjob')
    def remove(self):
        jobid = self.request.matchdict.get('jobid')
        if jobid is not None:
            job = self.db.jobs.find_one({'identifier': jobid})
            self.db.jobs.remove({'identifier': jobid})
            self.session.flash("Job %s deleted." % job['title'], queue='info')
        return {}

    def breadcrumbs(self):
        breadcrumbs = super(MyJobs, self).breadcrumbs()
        breadcrumbs.append(dict(route_name='myjobs', title=self.title))
        return breadcrumbs
    
    @view_config(route_name='myjobs', renderer='phoenix:templates/myjobs.pt')
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
        self.column_formats['creation_time'] = self.creation_time_td
        self.column_formats['status'] = self.status_td
        self.column_formats['title'] = self.title_td
        self.column_formats['progress'] = self.progress_td
        self.column_formats[''] = self.action_td

    def creation_time_td(self, col_num, i, item):
        return self.render_timestamp_td(item.get('creation_time'))

    def status_td(self, col_num, i, item):
        # TODO: status message is not updated by javascript

        status = item.get('status')
        if status is None:
            return HTML.td('')
        span_class = 'label'
        if status == 'ProcessSucceeded':
            span_class += ' label-success'
        elif status == 'ProcessFailed':
            span_class += ' label-warning'
        elif status == 'Exception':
            span_class += ' label-important'
        else:
            span_class += ' label-info'
        div = Template("""\
        <div>
          <div>
            <span class="${span_class}" id="status-${jobid}">${status}</span>
            <div id="message-${jobid}">${status_message}</div>
          </div>
          <div>
             <a class="label label-warning" href="${status_location}" data-format="XML">XML</a>
          </div>
        </div>
        """)
        return HTML.td(HTML.literal(div.substitute( {
            'jobid': item['identifier'],
            'status': item['status'],
            'span_class': span_class,
            'status_message': item['status_message'], 
            'status_location': item['status_location']} )))

    def title_td(self, col_num, i, item):
        return self.render_title_td(item['title'], item['abstract'], item['keywords'].split(','))

    def progress_td(self, col_num, i, item):
        """Generate the column for the job progress.
        """
        progress = item.get('progress', 100)
        if progress is None:
            return HTML.td('')
        span_class = 'progress progress-info bar'

        div_bar = HTML.tag(
            "div",
            c=HTML.literal(progress),
            class_="bar",
            style_="width: %d%s" % (progress, '%'),
            id_="progress-%s" % item.get('identifier'))
        div_progress = HTML.tag(
            "div",
            c=div_bar,
            class_="progress progress-info")
       
        return HTML.td(div_progress)
   
    def action_td(self, col_num, i, item):
        buttongroup = []
        buttongroup.append( ("show", item.get('identifier'), "icon-th-list", "Show Outputs", "#") )
        buttongroup.append( ("remove", item.get('identifier'), "icon-trash", "Delete", "#") )
        return self.render_action_td(buttongroup)

