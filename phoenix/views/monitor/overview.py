from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPException, HTTPFound, HTTPNotFound
from pyramid.security import authenticated_userid
from phoenix.views.monitor import Monitor

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
        return list(self.jobsdb.find({'email': authenticated_userid(self.request)}).sort('created', -1))

    @view_config(route_name='remove_myjobs')
    def remove_all(self):
        count = self.jobsdb.find({'email': authenticated_userid(self.request)}).count()
        self.jobsdb.remove({'email': authenticated_userid(self.request)})
        self.session.flash("%d Jobs deleted." % count, queue='info')
        return HTTPFound(location=self.request.route_path(self.name))

    @view_config(route_name='remove_job')
    def remove(self):
        jobid = self.request.matchdict.get('jobid')
        if jobid is not None:
            job = self.jobsdb.find_one({'identifier': jobid})
            self.jobsdb.remove({'identifier': jobid})
            self.session.flash("Job %s deleted." % job['title'], queue='info')
        return HTTPFound(location=self.request.route_path(self.name))

    @view_config(route_name='monitor', renderer='phoenix:templates/monitor/overview.pt')
    def view(self):
        items = self.update_jobs()

        from phoenix.grid.jobs import JobsGrid
        grid = JobsGrid(self.request, items,
                ['status', 'job', 'duration', 'finished', 'progress', ''],
            )
        return dict(grid=grid)



