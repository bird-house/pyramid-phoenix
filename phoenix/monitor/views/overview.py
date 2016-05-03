from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPException, HTTPFound, HTTPNotFound
from pyramid.security import authenticated_userid
from phoenix.monitor.views import Monitor
from phoenix.grid import MyGrid

import logging
logger = logging.getLogger(__name__)

class Overview(Monitor):
    def __init__(self, request):
        super(Overview, self).__init__(request, name='monitor', title='Overview')
        self.jobsdb = self.request.db.jobs

    def breadcrumbs(self):
        breadcrumbs = super(Overview, self).breadcrumbs()
        return breadcrumbs

    @view_config(renderer='json', route_name='update_myjobs')
    def update_jobs(self, category='public'):
        search_filter =  { 'userid': authenticated_userid(self.request) }
        if category == 'private':
            search_filter['public'] = False
        return list(self.jobsdb.find(search_filter).sort('created', -1))

    @view_config(route_name='monitor', renderer='../templates/monitor/overview.pt')
    def view(self):
        page = int(self.request.params.get('page', '0'))
        category = self.request.params.get('category')

        items = self.update_jobs()

        grid = JobsGrid(self.request, items,
                ['status', 'job', 'userid', 'process', 'service', 'duration', 'finished', 'public', 'progress'],
            )
        return dict(grid=grid, category=category, selected_status='All', page=page, start=0, end=0, hits=0)

class JobsGrid(MyGrid):
    def __init__(self, request, *args, **kwargs):
        super(JobsGrid, self).__init__(request, *args, **kwargs)
        self.column_formats['status'] = self.status_td
        self.column_formats['job'] = self.uuid_td
        self.column_formats['userid'] = self.userid_td
        self.column_formats['process'] = self.process_td
        self.column_formats['service'] = self.service_td
        self.column_formats['duration'] = self.duration_td
        self.column_formats['finished'] = self.finished_td
        self.column_formats['public'] = self.public_td
        self.column_formats['progress'] = self.progress_td
        self.exclude_ordering = self.columns

    def status_td(self, col_num, i, item):
        return self.render_status_td(item)

    def uuid_td(self, col_num, i, item):
        return self.render_button_td(
            url=self.request.route_path('monitor_details', tab='log', job_id=item.get('identifier')),
            title=item.get('identifier'))
    
    def userid_td(self, col_num, i, item):
        #TODO: avoid database access ... maybe store additional info at job
        userid = item.get('userid')
        provider_id = 'Unknown'
        if userid:
            user = self.request.db.users.find_one(dict(identifier=userid))
            if user:
                provider_id = user.get('login_id')
        return self.render_label_td(provider_id)
    
    def process_td(self, col_num, i, item):
        return self.render_label_td(item.get('title'))

    def service_td(self, col_num, i, item):
        return self.render_label_td(item.get('service'))

    def duration_td(self, col_num, i, item):
        return self.render_td(renderer="duration_td.mako",
                              duration=item.get('duration', "???"),
                              identifier=item.get('identifier'))
        
    def finished_td(self, col_num, i, item):
        return self.render_time_ago_td(item.get('finished'))

    def public_td(self, col_num, i, item):
        return self.render_td(renderer="public_td.mako", public=item.get('public', False))

    def progress_td(self, col_num, i, item):
        return self.render_progress_td(identifier=item.get('identifier'), progress = item.get('progress', 0))
        


