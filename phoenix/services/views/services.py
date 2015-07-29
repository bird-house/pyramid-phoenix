from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from phoenix.settings.views import SettingsView

import logging
logger = logging.getLogger(__name__)

class Services(SettingsView):
    def __init__(self, request):
        super(Services, self).__init__(
            request, name='services', title='Services')
        self.csw = self.request.csw

        
    def breadcrumbs(self):
        breadcrumbs = super(Services, self).breadcrumbs()
        breadcrumbs.append(dict(route_path=self.request.route_path(self.name), title=self.title))
        return breadcrumbs

    
    @view_config(route_name='service_details', renderer='../templates/services/service_details.pt')
    def details(self):
        service_id = self.request.matchdict.get('service_id')
        self.csw.getrecordbyid(id=[service_id])
        service = self.csw.records[service_id]
        return dict(service=service)

    
    @view_config(route_name='remove_service')
    def remove(self):
        try:
            service_id = self.request.matchdict.get('service_id')
            self.csw.getrecordbyid(id=[service_id])
            service=self.csw.records[service_id]
            self.csw.transaction(ttype='delete', typename='csw:Record', identifier=service_id )
            self.session.flash('Removed Service %s.' % service.title, queue="info")
        except Exception,e:
            msg = "Could not remove service %s" % e
            logger.exception(msg)
            self.session.flash(msg, queue="danger")
        return HTTPFound(location=self.request.route_path(self.name))

    
    @view_config(route_name="services", renderer='../templates/services/service_list.pt')
    def view(self):
        self.csw.getrecords2(esn="full", maxrecords=100)
        return dict(items=self.csw.records.values())


