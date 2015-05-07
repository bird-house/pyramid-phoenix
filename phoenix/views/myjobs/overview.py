from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPException, HTTPFound, HTTPNotFound

from phoenix.views.myjobs import MyJobs

import logging
logger = logging.getLogger(__name__)

@view_defaults(permission='edit', layout='default')
class Overview(MyJobs):
    def __init__(self, request):
        super(Overview, self).__init__(request, name='myjobs_overview', title='Overview')
        self.jobsdb = self.request.db.jobs

    def breadcrumbs(self):
        breadcrumbs = super(Overview, self).breadcrumbs()
        return breadcrumbs

    @view_config(renderer='json', route_name='update_myjobs')
    def update_jobs(self):
        from phoenix.models import update_job
        jobs = list(self.jobsdb.find({'email': self.user_email(), 'is_complete':False}))
        for job in jobs:
            update_job(self.request, job)
        return jobs

    @view_config(route_name='remove_myjobs')
    def remove_all(self):
        count = self.jobsdb.find({'email': self.user_email()}).count()
        self.jobsdb.remove({'email': self.user_email()})
        self.session.flash("%d Jobs deleted." % count, queue='info')
        return HTTPFound(location=self.request.route_path(self.name))

    @view_config(route_name='remove_myjob')
    def remove(self):
        jobid = self.request.matchdict.get('jobid')
        if jobid is not None:
            job = self.jobsdb.find_one({'identifier': jobid})
            self.jobsdb.remove({'identifier': jobid})
            self.session.flash("Job %s deleted." % job['title'], queue='info')
        return HTTPFound(location=self.request.route_path(self.name))

    @view_config(route_name='myjobs_overview', renderer='phoenix:templates/myjobs/overview.pt')
    def view(self):
        self.update_jobs()
        items = list(self.jobsdb.find({'email': self.user_email()}).sort('created', -1))

        from phoenix.grid.jobs import JobsGrid
        grid = JobsGrid(self.request, items,
                ['status', 'job', 'duration', 'finished', 'progress', ''],
            )
        return dict(grid=grid)



