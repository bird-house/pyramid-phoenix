import os
from pyramid.view import view_config, view_defaults
from pyramid.settings import asbool
from twitcher.registry import service_registry_factory
from mako.template import Template
import requests
from owslib.wms import WebMapService

import logging
logger = logging.getLogger(__name__)

map_script = Template(
    filename=os.path.join(os.path.dirname(__file__), "templates", "map", "map.js"),
    output_encoding="utf-8", input_encoding="utf-8")


@view_defaults(permission='view', layout='default')
class Map(object):
    def __init__(self, request):
        self.request = request
        self.session = self.request.session
        self.dataset = self.request.params.get('dataset')
        self.wms = self.get_wms()

    def get_wms(self):
        if not self.dataset:
            return None
        caps_url = self.request.route_url('owsproxy', service_name='wms',
                                          _query=[('dataset', self.dataset),
                                                  ('version', '1.1.1'), ('service', 'WMS'), ('request', 'GetCapabilities')])
        resp = requests.get(caps_url, verify=False)
        return WebMapService(caps_url, xml=resp.content)

    def get_layers(self):
        layers = list()
        for layer_id in list(self.wms.contents):
            if layer_id.endswith('/lat') or layer_id.endswith('/lon'):
                continue
            layers.append(layer_id)
        return layers

    @view_config(route_name='map', renderer='templates/map/map.pt')
    def view(self):
        layers = None
        if self.dataset:
            layers = self.get_layers()[0]
        
        text = map_script.render(
            url=self.request.registry.settings.get('wms.url'),
            dataset=self.dataset,
            layers=layers,
            styles="default-scalar/x-Rainbow",
            )
        return dict(map_script=text)


def includeme(config):
    settings = config.registry.settings

    logger.debug('Adding map ...')

    # init wms if available
    if asbool(settings.get('phoenix.wms', True)):
        logger.debug('Adding WMS ...')
        # configure ncwms
        service_registry = service_registry_factory(config.registry)
        service_registry.register_service(url=settings.get('wms.url'), name='wms', service_type='wms', public=True)

    def wms_activated(request):
        # settings = request.registry.settings
        return asbool(settings.get('phoenix.wms', True))
    config.add_request_method(wms_activated, reify=True)

    # views
    config.add_route('map', '/map')

