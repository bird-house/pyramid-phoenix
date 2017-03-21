from pyramid.view import view_defaults
from deform import Form

from phoenix.esgfsearch.schema import ESGFSearchSchema
from phoenix.esgfsearch.search import ESGFSearch

import logging
LOGGER = logging.getLogger(__name__)


@view_defaults(permission='view', layout='default')
class ESGFSearchActions(object):
    def __init__(self, request):
        self.request = request
        self.esgfsearch = ESGFSearch(request)

    def search_files(self):
        return self.esgfsearch.search_files()

    def search_datasets(self):
        result = dict(
            query=self.request.params.get('query', ''),
            selected=self.request.params.get('selected', 'project'),
            distrib=self.request.params.get('distrib', 'false'),
            replica=self.request.params.get('replica', 'false'),
            latest=self.request.params.get('latest', 'true'),
            temporal=str(self.esgfsearch.temporal).lower(),
            start=self.request.params.get('start', '2001'),
            end=self.request.params.get('end', '2005'),
            constraints=self.request.params.get('constraints', ''),
        )
        result.update(self.esgfsearch.search_datasets())
        result['form'] = Form(ESGFSearchSchema())
        result['quickview'] = True
        result['page'] = 0
        return result
