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
        self.session = self.request.session
        # TODO: fix wms registration
        self.request.wms

    def view(self):
        dataset = self.request.params.get('dataset')
        wms_url = self.request.params.get('wms_url')
        if dataset:
            use_proxy = False
            url = self.request.route_url(
                'owsproxy',
                service_name='wms',
                _query=[('DATASET', dataset)])
            caps_url = self.request.route_url(
                'owsproxy',
                service_name='wms',
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
            use_proxy = True
            try:
                wms = WebMapService(wms_url)
                map_name = wms_url.split('/')[-1]
            except:
                logger.exception("wms connect failed")
                raise Exception("could not connet to wms url %s", wms_url)
        else:
            wms = None
            map_name = None
            use_proxy = False
        return dict(map_script=map_script.render(wms=wms, dataset=dataset, use_proxy=use_proxy),
                    map_name=map_name)


def includeme(config):
    settings = config.registry.settings

    def map_activated(request):
        return asbool(settings.get('phoenix.map', 'false'))
    config.add_request_method(map_activated, reify=True)

    def wms_url(request):
        return settings.get('wms.url')
    config.add_request_method(wms_url, reify=True)

    if asbool(settings.get('phoenix.map', 'false')):
        config.include('phoenix.twitcherclient')

        # add wms service
        def get_wms(request):
            settings = request.registry.settings
            session = request.session
            if request.map_activated and 'wms' not in session:
                logger.debug('register wms service')
                try:
                    service_name = 'wms'
                    registry = twitcher_service_factory(request.registry)
                    logger.debug("register: name=%s, url=%s", service_name, settings['wms.url'])
                    registry.register_service(name=service_name, url=settings['wms.url'],
                                              public=True, service_type='wms',
                                              overwrite=True)
                    #session['wms'] = WebMapService(url=settings['wms.url'])
                    session['wms'] = settings['wms.url']
                except:
                    logger.exception('Could not connect wms %s', settings['wms.url'])
            return session.get('wms')
        config.add_request_method(get_wms, 'wms', reify=True)

        # map view
        config.add_route('map', '/map')
        config.add_view('phoenix.map.Map',
                        route_name='map',
                        attr='view',
                        renderer='templates/map/map.pt')
