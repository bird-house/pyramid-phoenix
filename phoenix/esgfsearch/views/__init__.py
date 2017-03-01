from pyramid.view import view_defaults

from phoenix.esgfsearch.schema import ESGFSearchSchema


@view_defaults(permission='view', layout='default')
class ESGFSearch(object):
    def __init__(self, request):
        self.request = request

    def view(self):
        return dict()
