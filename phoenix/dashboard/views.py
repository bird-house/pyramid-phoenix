from pyramid.view import view_config, view_defaults

from phoenix.views import MyView

import logging
logger = logging.getLogger(__name__)

@view_defaults(permission='view', layout='default')
class Dashboard(MyView):
    def __init__(self, request):
        super(Dashboard, self).__init__(request, name='dashboard', title='Dashboard')

    @view_config(route_name='dashboard', renderer='templates/dashboard/dashboard.pt')
    def view(self):
        tab = self.request.matchdict.get('tab', 'jobs')

        lm = self.request.layout_manager
        if tab == 'jobs':
            lm.layout.add_heading('dashboard_jobs')
        elif tab == 'users':
            lm.layout.add_heading('dashboard_users')
        return dict(active=tab)
