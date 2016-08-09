import os
from pyramid.view import view_config, view_defaults
from pyramid.settings import asbool
from mako.template import Template
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

    @view_config(route_name='map', renderer='templates/map/map.pt')
    def view(self):
        dataset = self.request.params.get('dataset')
        if dataset:
            wms = WebMapService(self.request.wms_url + '?DATASET=' + dataset)
        else:
            wms = None
        return dict(map_script=map_script.render(wms=wms, dataset=dataset))


def includeme(config):
    settings = config.registry.settings

    logger.debug('Adding map ...')

    def wms_activated(request):
        return asbool(settings.get('phoenix.wms', True))
    config.add_request_method(wms_activated, reify=True)

    def wms_url(request):
        return settings.get('wms.url')
    config.add_request_method(wms_url, reify=True)

    # views
    config.add_route('map', '/map')

