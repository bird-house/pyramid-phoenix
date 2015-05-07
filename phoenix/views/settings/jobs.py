from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from phoenix.views.settings import SettingsView

import logging
logger = logging.getLogger(__name__)

class Jobs(SettingsView):
    def __init__(self, request):
        super(Jobs, self).__init__(request, name='settings_jobs', title='Jobs')
        self.jobsdb = self.request.db.jobs

    def breadcrumbs(self):
        breadcrumbs = super(Jobs, self).breadcrumbs()
        breadcrumbs.append(dict(route_path=self.request.route_path(self.name), title=self.title))
        return breadcrumbs

    @view_config(route_name='remove_all_jobs')
    def remove_all(self):
        count = self.jobsdb.count()
        self.jobsdb.drop()
        self.session.flash("%d Jobs deleted." % count, queue='info')
        return HTTPFound(location=self.request.route_url(self.name))

    @view_config(route_name='settings_jobs', renderer='phoenix:templates/settings/jobs.pt')
    def view(self):
        jobs = list(self.jobsdb.find().sort('created', -1))
        grid = JobsGrid(self.request, jobs,
                ['status', 'job', 'email', 'duration', 'finished', 'progress', ''],
            )
        return dict(grid=grid)

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
        return self.render_td(renderer="duration_td",
                              duration=item.get('duration', "???"),
                              identifier=item.get('identifier'))
        
    def finished_td(self, col_num, i, item):
        return self.render_time_ago_td(item.get('finished'))

    def progress_td(self, col_num, i, item):
        return self.render_progress_td(identifier=item.get('identifier'), progress = item.get('progress', 0))
        
    def action_td(self, col_num, i, item):
        buttongroup = []
        buttongroup.append( ("remove", item.get('identifier'), "glyphicon glyphicon-trash text-danger", "Remove Job", 
                             self.request.route_path('remove_myjob', jobid=item.get('identifier')), False) )
        return self.render_action_td(buttongroup)

