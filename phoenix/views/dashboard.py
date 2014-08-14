from pyramid.view import view_config, view_defaults

from phoenix.views.views import MyView

import logging
logger = logging.getLogger(__name__)

@view_defaults(permission='view', layout='default')
class Dashboard(MyView):
    def __init__(self, request):
        super(Dashboard, self).__init__(request, 'Dashboard')

    @view_config(route_name='dashboard', renderer='phoenix:templates/dashboard.pt')
    def view(self):
        lm = self.request.layout_manager
        lm.layout.add_heading('dashboard_users')

        return dict()
