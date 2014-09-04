from pyramid.view import view_config

from pyramid.httpexceptions import HTTPException, HTTPFound, HTTPNotFound
from deform import Form, Button
from deform import ValidationFailure

from phoenix.views.settings import SettingsView
from phoenix.grid import MyGrid

import logging
logger = logging.getLogger(__name__)

class Jobs(SettingsView):
    def __init__(self, request):
        super(Jobs, self).__init__(request, name='job_settings', title='Jobs')
        self.jobsdb = self.request.db.jobs 

    @view_config(route_name='remove_all_jobs')
    def remove(self):
        count = self.jobsdb.count()
        self.jobsdb.drop()
        self.session.flash("%d Jobs deleted." % count, queue='info')
        return HTTPFound(location=self.request.route_url('job_settings'))

    @view_config(route_name='job_settings', renderer='phoenix:templates/settings/jobs.pt')
    def view(self):
        return {}

