from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPException, HTTPFound, HTTPNotFound
from pyramid.security import authenticated_userid
from phoenix.monitor.views import Monitor

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
    def update_jobs(self):
        return list(self.jobsdb.find({'userid': authenticated_userid(self.request)}).sort('created', -1))

    @view_config(route_name='monitor', renderer='../templates/monitor/overview.pt')
    def view(self):
        items = self.update_jobs()

        from phoenix.grid.jobs import JobsGrid
        grid = JobsGrid(self.request, items,
                ['status', 'job', 'process', 'service', 'duration', 'finished', 'progress'],
            )
        return dict(grid=grid)



