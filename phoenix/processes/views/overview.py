from pyramid.view import view_config, view_defaults

from phoenix.catalog import WPS_TYPE
from phoenix.views import MyView

import logging
logger = logging.getLogger(__name__)


@view_defaults(permission='view', layout="default")
class Overview(MyView):
    def __init__(self, request):
        super(Overview, self).__init__(request, name='processes', title='')

    @view_config(route_name='processes', renderer='../templates/processes/overview.pt')
    def view(self):
        items = []
        for service in self.request.catalog.get_services(service_type=WPS_TYPE):
            # TODO: get name from service object
            service_name = self.request.catalog.get_service_name(service)
            url = self.request.route_path('processes_list', _query=[('wps', service_name)])
            items.append(dict(title=service.title, description=service.abstract, public=service.public, url=url))
        return dict(title="Web Processing Services", items=items)
