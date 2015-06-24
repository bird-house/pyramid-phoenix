from pyramid.view import view_config, view_defaults

import logging
logger = logging.getLogger(__name__)

@view_defaults(permission='view', layout='default')
class Home(object):
    def __init__(self, request):
        self.request = request
        self.session = self.request.session

    @view_config(route_name='home', renderer='phoenix:templates/home.pt')
    def view(self):
        return {}
