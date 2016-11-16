from pyramid.view import view_config, view_defaults

from phoenix.processes.views.list import ProcessList

import logging
logger = logging.getLogger(__name__)

@view_defaults(permission='view', layout="default")
class ProcessListJson(ProcessList):
    def __init__(self, request):
        ProcessList.__init__(self, request)

    @view_config(route_name='processes_list', renderer='json', accept='application/json')
    def view(self):
        return ProcessList.view(self)

