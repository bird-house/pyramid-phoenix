from pyramid.view import view_config, view_defaults

from phoenix.views import MyView


@view_defaults(permission='admin', layout='default')
class Services(MyView):
    def __init__(self, request):
        super(Services, self).__init__(
            request, name='services', title='Services')

    @view_config(route_name='service_details', renderer='phoenix:services/templates/services/service_details.pt')
    def details_view(self):
        service_id = self.request.matchdict.get('service_id')
        service = self.request.catalog.get_record_by_id(service_id)
        return dict(service=service, service_name=service.title)

    @view_config(route_name="services", renderer='phoenix:services/templates/services/service_list.pt')
    def list_view(self):
        return dict(items=self.request.catalog.get_services())
