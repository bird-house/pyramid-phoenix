from pyramid.view import view_config, view_defaults

from pyramid.httpexceptions import HTTPException, HTTPFound, HTTPNotFound
from deform import Form, Button
from deform import ValidationFailure

from string import Template
from webhelpers.html.builder import HTML

from phoenix.grid import MyGrid
from phoenix.views import MyView
from phoenix.utils import localize_datetime

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
        
        grid = JobsGrid(
                self.request,
                items,
                ['status', 'creation_time', 'title', 'status_message', 'progress', ''],
            )
        return dict(grid=grid, items=items)


class JobsGrid(MyGrid):
    def __init__(self, request, *args, **kwargs):
        super(JobsGrid, self).__init__(request, *args, **kwargs)
        self.column_formats['creation_time'] = self.creation_time_td
        self.column_formats['status'] = self.status_td
        self.column_formats['title'] = self.title_td
        self.column_formats['status_message'] = self.message_td
        self.column_formats['progress'] = self.progress_td
        self.column_formats[''] = self.action_td
        self.exclude_ordering = ['status_message', 'action']

    def creation_time_td(self, col_num, i, item):
        if item.get('creation_time') is None:
            return HTML.td('')
        span_class = 'due-date badge'
        #if item.start_time:
        #    span_class += ' badge-important'
        creation_time = localize_datetime(item.get('creation_time'), self.user_tz)
        span = HTML.tag(
            "span",
            c=HTML.literal(creation_time.strftime('%Y-%m-%d %H:%M:%S')),
            class_=span_class,
        )
        return HTML.td(span)

    def status_td(self, col_num, i, item):
        """Generate the column for the job status.
        """
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
            
        span = HTML.tag(
            "span",
            c=HTML.literal(status),
            class_=span_class,
            id_="status-%s" % item.get('identifier'))
        return HTML.td(span)

    def title_td(self, col_num, i, item):
        keyword_links = []
        for keyword in item.get('tags').split(','):
            anchor = HTML.tag("a", href="#", c=keyword, class_="label label-info")
            keyword_links.append(anchor)
        
        div = Template("""\
        <div class="">
          <div class="">
            <b>${title}</b>
            <div>${abstract}</div>
          </div>
          <div>${keywords}</div>
        </div>
        """)
        return HTML.td(HTML.literal(div.substitute( {'title': item['title'], 'abstract': item['notes'], 'keywords': ' '.join(keyword_links)} )))

    def message_td(self, col_num, i, item):
        div = Template("""\
        <div class="">
          <div class="">
            <div>${status_message}</div>
          </div>
          <div>
             <a class="label label-warning" href="${status_location}" data-format="XML">XML</a>
          </div>
        </div>
        """)
        return HTML.td(HTML.literal(div.substitute( {'status_message': item['status_message'], 'status_location': item['status_location']} )))

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
        """Generate the column that has the actions in it.
        """
        div = Template("""\
        <div class="btn-group">
          <a class="btn dropdown-toggle" data-toggle="dropdown" href="#">Action<span class="caret"></span></a>
          <ul class="dropdown-menu">
            <!-- dropdown menu links -->
            <li><a class="show" data-value="${jobid}"><i class="icon-th-list"></i> Show Outputs</a></li>
            <li><a class="delete" data-value="${jobid}"><i class="icon-trash"></i> Delete</a></li>
          </ul>
        </div>
        """)
        return HTML.td(HTML.literal(div.substitute({'jobid': item.get('identifier')} )))

