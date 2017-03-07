from pyramid.view import view_defaults
from deform import Form

from phoenix.esgfsearch.schema import ESGFSearchSchema
from phoenix.esgfsearch.search import search


@view_defaults(permission='view', layout='default')
class ESGFSearch(object):
    def __init__(self, request):
        self.request = request

    def view(self):
        result = dict(
            query=self.request.params.get('query', ''),
            selected=self.request.params.get('selected', 'project'),
            distrib=self.request.params.get('distrib', 'false'),
            replica=self.request.params.get('replica', 'false'),
            latest=self.request.params.get('latest', 'true'),
            temporal=self.request.params.get('temporal', 'true'),
            start=self.request.params.get('start', '2001'),
            end=self.request.params.get('end', '2005'),
            constraints=self.request.params.get('constraints', ''),
        )
        result.update(search(self.request))
        result['form'] = Form(ESGFSearchSchema())
        result['quickview'] = True
        return result
