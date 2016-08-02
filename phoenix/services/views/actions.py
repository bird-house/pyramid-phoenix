from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound

from twitcher.registry import service_registry_factory

import logging
logger = logging.getLogger(__name__)


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
            service = self.request.catalog.get_record_by_id(service_id)
            self.request.catalog.delete_record(service_id)
            # TODO: use events to unregister service
            registry = service_registry_factory(self.request.registry)
            # TODO: fix service name
            registry.unregister_service(name=service.title.lower())
            self.session.flash('Removed Service %s.' % service.title, queue="info")
        except Exception,e:
            msg = "Could not remove service %s" % e
            logger.exception(msg)
            self.session.flash(msg, queue="danger")
        return HTTPFound(location=self.request.route_path('services'))


def includeme(config):
    """ Pyramid includeme hook.

    :param config: app config
    :type config: :class:`pyramid.config.Configurator`
    """

    config.add_route('remove_service', '/services/{service_id}/remove')
