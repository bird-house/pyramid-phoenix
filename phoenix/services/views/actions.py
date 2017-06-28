from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound

import logging
LOGGER = logging.getLogger("PHOENIX")


@view_defaults(permission='submit')
class ServiceActions(object):
    """Actions related to service registration."""

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.session = self.request.session

    @view_config(route_name='remove_service')
    def remove_service(self):
        try:
            service_id = self.request.matchdict.get('service_id')
            self.request.catalog.delete_record(service_id)
            self.session.flash('Removed Service.', queue="info")
        except Exception, e:
            self.session.flash("Could not remove service.", queue="danger")
        return HTTPFound(location=self.request.route_path('services'))

    @view_config(route_name='clear_services')
    def clear_services(self):
        try:
            self.request.catalog.clear_services()
            self.session.flash('All Service removed.', queue="info")
        except Exception, e:
            self.session.flash("Could not remove services.", queue="danger")
        return HTTPFound(location=self.request.route_path('services'))


def includeme(config):
    """ Pyramid includeme hook.

    :param config: app config
    :type config: :class:`pyramid.config.Configurator`
    """

    config.add_route('clear_services', '/clear_services')
    config.add_route('remove_service', '/services/{service_id}/remove')
