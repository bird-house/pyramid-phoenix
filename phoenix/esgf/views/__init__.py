from pyramid.view import view_defaults
from deform import Form

from phoenix.esgf.schema import ESGFLogonSchema
from phoenix.esgf.schema import ESGFSearchSchema
from phoenix.esgf.search import ESGFSearch

import logging
LOGGER = logging.getLogger("PHOENIX")


@view_defaults(permission='edit', layout='default')
class ESGFLogon(object):
    def __init__(self, request):
        self.request = request

    def view(self):
        return {}


@view_defaults(permission='view', layout='default')
class ESGFSearchActions(object):
    def __init__(self, request):
        self.request = request
        self.esgfsearch = ESGFSearch(request)

    def search_datasets(self):
        result = dict()
        result.update(self.esgfsearch.query_params())
        result.update(self.esgfsearch.search_datasets())
        result['form'] = Form(ESGFSearchSchema())
        result['quickview'] = True
        return result

    def search_items(self):
        return self.esgfsearch.search_items()
