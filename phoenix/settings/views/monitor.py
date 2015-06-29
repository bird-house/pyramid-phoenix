from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from . import SettingsView

import logging
logger = logging.getLogger(__name__)

class Jobs(SettingsView):
    def __init__(self, request):
        super(Jobs, self).__init__(request, name='settings_monitor', title='Monitor')
        self.jobsdb = self.request.db.jobs

    def breadcrumbs(self):
        breadcrumbs = super(Jobs, self).breadcrumbs()
        breadcrumbs.append(dict(route_path=self.request.route_path(self.name), title=self.title))
        return breadcrumbs

    @view_config(route_name='settings_monitor', renderer='../templates/settings/monitor.pt')
    def view(self):
        jobs = list(self.jobsdb.find().sort('created', -1))
        
        from phoenix.grid.jobs import JobsGrid
        grid = JobsGrid(self.request, jobs,
                ['status', 'job', 'userid', 'duration', 'finished', 'progress'],
            )
        return dict(grid=grid)


