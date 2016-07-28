import os
from pyramid.view import view_config, view_defaults
from twitcher.registry import service_registry_factory
from mako.template import Template

import logging
logger = logging.getLogger(__name__)

map_script = Template(
    filename=os.path.join(os.path.dirname(__file__), "templates", "map.js"),
    output_encoding="utf-8", input_encoding="utf-8")


@view_defaults(permission='view', layout='default')
class Map(object):
    def __init__(self, request):
        self.request = request
        self.session = self.request.session
        self.dataset = self.request.params.get('dataset')

    @view_config(route_name='map', renderer='phoenix:templates/map.pt')
    def view(self):
        text = map_script.render(
            dataset="outputs/hummingbird/output-3d059bc0-5033-11e6-9fa2-af0ebe9e921e.nc",
            layers="tasmax",
            styles="default-scalar/x-Rainbow",
            )
        return dict(map_script=text)

def includeme(config):
    settings = config.registry.settings

    logger.info('Adding map ...')

    # views
    config.add_route('map', '/map')

    # configure ncwms
    ncwms_url = settings.get('wms.url')
    service_registry = service_registry_factory(config.registry)
    service_registry.register_service(url=ncwms_url + '/wms', name='wms', service_type='wms', public=True)



    
