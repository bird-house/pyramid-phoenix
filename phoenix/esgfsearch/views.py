from pyramid.view import view_defaults


import logging
logger = logging.getLogger(__name__)


@view_defaults(permission='view', layout='default')
class ESGFSearch(object):
    def __init__(self, request):
        self.request = request

    def view(self):
        return dict()
