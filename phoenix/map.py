from pyramid.view import view_config, view_defaults
from twitcher.registry import service_registry_factory

import logging
logger = logging.getLogger(__name__)


@view_defaults(permission='view', layout='default')
class Map(object):
    def __init__(self, request):
        self.request = request
        self.session = self.request.session

    @view_config(route_name='map', renderer='phoenix:templates/map.pt')
    def view(self):
        service_registry = service_registry_factory(self.request.registry)
        ncwms_url = self.request.registry.settings.get('wms.url')
        service_registry.register_service(url=ncwms_url + '/wms', name='wms', service_type='wms', public=True)
        return {}

def includeme(config):
    settings = config.registry.settings

    logger.info('Adding map ...')

    # views
    config.add_route('map', '/map')



    
