from pyramid.view import view_config, view_defaults

from phoenix.views import MyView

import logging
logger = logging.getLogger(__name__)


@view_defaults(permission='view', layout='default')
class Details(MyView):
    def __init__(self, request):
        super(Details, self).__init__(
            request, name='monitor_details', title='Details')

    @view_config(route_name='monitor_details', renderer='../templates/monitor/details.pt')
    def view(self):
        tab = self.request.matchdict.get('tab')
        job_id = self.request.matchdict.get('job_id')
        collection = self.request.db.jobs
        job = collection.find_one({'identifier': job_id})
        return dict(active=tab, job_id=job_id, status=job['status'])
