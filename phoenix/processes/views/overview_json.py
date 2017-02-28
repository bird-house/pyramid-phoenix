from pyramid.view import view_config, view_defaults

from phoenix.processes.views.overview import Overview

import logging
logger = logging.getLogger(__name__)

@view_defaults(permission='view', layout="default")
class OverviewJson(Overview):
    def __init__(self, request):
        Overview.__init__(self, request)

    @view_config(route_name='processes', renderer='json', accept='application/json')
    def view(self):
        return Overview.view(self)
