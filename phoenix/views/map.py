from pyramid.view import view_config, view_defaults

import logging
logger = logging.getLogger(__name__)

@view_defaults(permission='edit', layout='default') 
class Map:
    def __init__(self, request):
        self.request = request

    @view_config(route_name='map', renderer='phoenix:templates/map.pt')
    def map(self):
        return dict()
