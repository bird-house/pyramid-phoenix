from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from twitcher.registry import service_registry_factory

from phoenix.settings.views import SettingsView

import logging
logger = logging.getLogger(__name__)

class Services(SettingsView):
    def __init__(self, request):
        super(Services, self).__init__(
            request, name='services', title='Services')
        
    def breadcrumbs(self):
        breadcrumbs = super(Services, self).breadcrumbs()
        breadcrumbs.append(dict(route_path=self.request.route_path(self.name), title=self.title))
        return breadcrumbs

    
    @view_config(route_name='service_details', renderer='../templates/services/service_details.pt')
    def details(self):
        service_id = self.request.matchdict.get('service_id')
        service = self.request.catalog.get_record_by_id(service_id)
        return dict(service=service)

    
    @view_config(route_name='remove_service')
    def remove(self):
        try:
            service_id = self.request.matchdict.get('service_id')
            service = self.request.catalog.get_record_by_id(service_id)
            self.request.catalog.delete(service_id)
            # TODO: use events to unregister service
            registry = service_registry_factory(self.request.registry)
            # TODO: fix service name
            registry.unregister_service(name=service.title.lower())
            self.session.flash('Removed Service %s.' % service.title, queue="info")
        except Exception,e:
            msg = "Could not remove service %s" % e
            logger.exception(msg)
            self.session.flash(msg, queue="danger")
        return HTTPFound(location=self.request.route_path(self.name))

    
    @view_config(route_name="services", renderer='../templates/services/service_list.pt')
    def view(self):
        return dict(items=self.request.catalog.get_services())


