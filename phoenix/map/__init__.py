import os
import requests
from pyramid.view import view_config, view_defaults
from pyramid.settings import asbool
from mako.template import Template
from owslib.wms import WebMapService
from twitcher.registry import service_registry_factory

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

    @view_config(route_name='map', renderer='templates/map/map.pt')
    def view(self):
        dataset = self.request.params.get('dataset')
        wms_url = self.request.params.get('wms_url')
        if dataset:
            url = self.request.route_url(
                'owsproxy',
                service_name='wms',
                _query=[('DATASET', dataset)])
            caps_url = self.request.route_url(
                'owsproxy',
                service_name='wms',
                _query=[('DATASET', dataset),
                        ('service', 'WMS'), ('request', 'GetCapabilities'), ('version', '1.1.1')])
            response = requests.get(caps_url, verify=False)
            wms = WebMapService(url, version='1.1.1', xml=response.content)
            map_name = dataset.split('/')[-1]
            use_proxy = False
        elif wms_url:
            wms = WebMapService(wms_url)
            map_name = wms_url.split('/')[-1]
            use_proxy = True
        else:
            wms = None
            map_name = None
            use_proxy = False
        return dict(map_script=map_script.render(wms=wms, dataset=dataset, use_proxy=use_proxy),
                    map_name=map_name)


def includeme(config):
    settings = config.registry.settings

    # logger.debug('Adding map ...')

    def wms_activated(request):
        return asbool(settings.get('phoenix.wms', 'false'))
    config.add_request_method(wms_activated, reify=True)

    def wms_url(request):
        return settings.get('wms.url')
    config.add_request_method(wms_url, reify=True)

    if asbool(settings.get('phoenix.wms', 'false')):
        url = settings.get('wms.url')
        service_registry = service_registry_factory(config.registry)
        try:
            service_registry.get_service_by_url(url)
        except ValueError:
            service_registry.register_service(url, name="wms", public=True, service_type='wms')
    # views
    config.add_route('map', '/map')

