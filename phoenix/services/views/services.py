from pyramid.view import view_config, view_defaults

from phoenix.catalog import WPS_TYPE
from phoenix.views import MyView

import logging
logger = logging.getLogger(__name__)


@view_defaults(permission='admin', layout='default')
class Services(MyView):
    def __init__(self, request):
        super(Services, self).__init__(
            request, name='services', title='Services')

    def breadcrumbs(self):
        breadcrumbs = super(Services, self).breadcrumbs()
        breadcrumbs.append(dict(route_path=self.request.route_path('settings'), title="Settings"))
        breadcrumbs.append(dict(route_path=self.request.route_path(self.name), title=self.title))
        return breadcrumbs

    @view_config(route_name='service_details', renderer='../templates/services/service_details.pt')
    def details_view(self):
        service_id = self.request.matchdict.get('service_id')
        service = self.request.catalog.get_record_by_id(service_id)
        if service.format == WPS_TYPE:
            try:
                service_name = self.request.catalog.get_service_name(service)
            except Exception, err:
                self.session.flash("Error: This service is not available.", queue='danger')
                service_name = 'unknown'
        return dict(service=service, service_name=service_name)

    @view_config(route_name="services", renderer='../templates/services/service_list.pt')
    def list_view(self):
        return dict(items=self.request.catalog.get_services())
