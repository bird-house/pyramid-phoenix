from pyramid.view import view_config, view_defaults

from phoenix.views import MyView


@view_defaults(permission='view', layout='default')
class Details(MyView):
    def __init__(self, request):
        super(Details, self).__init__(request, name='job_details', title='Job Details')
        self.tab = self.request.matchdict.get('tab')
        self.job_id = self.request.matchdict.get('job_id')
        self.collection = self.request.db.jobs

    @view_config(route_name='job_details', renderer='phoenix:monitor/templates/monitor/details.pt')
    def view(self):
        status = 'ProcessAccepted'
        if self.collection.find({"identifier": self.job_id}).count() == 1:
            job = self.collection.find_one({'identifier': self.job_id})
            status = job["status"]
        return dict(active=self.tab, job_id=self.job_id, status=status)
