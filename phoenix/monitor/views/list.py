from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPException, HTTPFound, HTTPNotFound
from pyramid.security import authenticated_userid

from phoenix.grid import CustomGrid
from phoenix.monitor.views import Monitor
from phoenix.monitor.views.actions import monitor_buttons

import logging
logger = logging.getLogger(__name__)

class JobList(Monitor):
    def __init__(self, request):
        super(JobList, self).__init__(request, name='monitor', title='Job List')
        self.db = self.request.db.jobs

    def breadcrumbs(self):
        breadcrumbs = super(JobList, self).breadcrumbs()
        return breadcrumbs

    @view_config(renderer='json', route_name='update_myjobs')
    def update_jobs(self, page=0, limit=10, access=None, status=None):
        search_filter =  {}
        if access == 'public':
            search_filter['access'] = 'public'
        elif access == 'private':
            search_filter['access'] = 'private'
            search_filter['userid'] = authenticated_userid(self.request)
        elif access == 'all' and self.request.has_permission('admin'):
            pass
        else:
            search_filter['userid'] = authenticated_userid(self.request)
        if status:
            search_filter['status'] = status
        count = self.db.find(search_filter).count()
        items = list(self.db.find(search_filter).skip(page*limit).limit(limit).sort('created', -1))
        return items, count

    @view_config(route_name='monitor', renderer='../templates/monitor/list.pt')
    def view(self):
        page = int(self.request.params.get('page', '0'))
        limit = int(self.request.params.get('limit', '10'))
        access = self.request.params.get('access')
        status = self.request.params.get('status')

        buttons = monitor_buttons(self.context, self.request)
        for button in buttons:
            if button.name in self.request.POST:
                children = self.request.POST.getall('children')
                self.session['phoenix.selected-children'] = children
                self.session.changed()
                location = button.url(self.context, self.request)
                logger.debug("button url = %s", location)
                return HTTPFound(location, request=self.request)
        
        items, count = self.update_jobs(page=page, limit=limit, access=access, status=status)

        grid = JobsGrid(self.request, items,
                    ['_checkbox', 'status', 'job', 'userid', 'process', 'service', 'duration', 'finished', 'public', 'progress'],
                    )
        return dict(grid=grid, access=access, status=status, page=page, limit=limit, count=count,
                    buttons=buttons)

class JobsGrid(CustomGrid):
    def __init__(self, request, *args, **kwargs):
        super(JobsGrid, self).__init__(request, *args, **kwargs)
        self.column_formats['status'] = self.status_td
        self.column_formats['job'] = self.uuid_td
        self.column_formats['userid'] = self.userid_td('userid')
        self.column_formats['process'] = self.label_td('title')
        self.column_formats['duration'] = self.label_td('duration', '???')
        self.column_formats['finished'] = self.time_ago_td('finished')
        self.column_formats['public'] = self.access_td
        self.column_formats['progress'] = self.progress_td('progress')
        self.exclude_ordering = self.columns
        
    def status_td(self, col_num, i, item):
        return self.render_status_td(item)

    def uuid_td(self, col_num, i, item):
        return self.render_button_td(
            url=self.request.route_path('monitor_details', tab='log', job_id=item.get('identifier')),
            title=item.get('identifier'))
    
    def access_td(self, col_num, i, item):
        return self.render_td(renderer="access_td.mako", access=item.get('access', 'private'))

        


