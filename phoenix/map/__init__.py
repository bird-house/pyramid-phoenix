import os
import requests

from pyramid.view import view_config, view_defaults
from pyramid.settings import asbool
from pyramid.events import NewRequest
from mako.template import Template
from owslib.wms import WebMapService

from phoenix.twitcherclient import twitcher_service_factory

import logging
logger = logging.getLogger(__name__)

map_script = Template(
    filename=os.path.join(os.path.dirname(__file__), "templates", "map", "map.js"),
    output_encoding="utf-8", input_encoding="utf-8")


@view_defaults(permission='view', layout='default')
class Map(object):
    def __init__(self, request):
        self.request = request

    def view(self):
        dataset = self.request.params.get('dataset')
        wms_url = self.request.params.get('wms_url')
        if dataset:
            url = self.request.route_url(
                'wms',
                _query=[('DATASET', dataset)])
            caps_url = self.request.route_url(
                'wms',
                _query=[('DATASET', dataset),
                        ('service', 'WMS'), ('request', 'GetCapabilities'), ('version', '1.1.1')])
            try:
                response = requests.get(caps_url, verify=False)
                if not response.ok:
                    raise Exception("get caps failed: url=%s", caps_url)
                wms = WebMapService(url, version='1.1.1', xml=response.content)
                map_name = dataset.split('/')[-1]
            except:
                logger.exception("wms connect failed")
                raise Exception("could not connect to wms url %s", caps_url)
        elif wms_url:
            try:
                wms = WebMapService(wms_url)
                map_name = wms_url.split('/')[-1]
            except:
                logger.exception("wms connect failed")
                raise Exception("could not connet to wms url %s", wms_url)
        else:
            wms = None
            map_name = None
        return dict(map_script=map_script.render(wms=wms, dataset=dataset),
                    map_name=map_name)


def includeme(config):
    settings = config.registry.settings

    def map_activated(request):
        return asbool(settings.get('phoenix.map', 'false'))
    config.add_request_method(map_activated, reify=True)

    if asbool(settings.get('phoenix.map', 'false')):
        # wms url
        config.add_route('wms', settings['wms.url'])

        # map view
        config.add_route('map', '/map')
        config.add_view('phoenix.map.Map',
                        route_name='map',
                        attr='view',
                        renderer='templates/map/map.pt')
