from pyramid.view import view_defaults
from deform import Form
from pyramid.settings import asbool

from pyesgf.search import SearchConnection
from pyesgf.search.consts import TYPE_DATASET, TYPE_AGGREGATION, TYPE_FILE

from phoenix.esgfsearch.schema import ESGFSearchSchema
from phoenix.esgfsearch.search import search


@view_defaults(permission='view', layout='default')
class ESGFSearch(object):
    def __init__(self, request):
        self.request = request
        settings = request.registry.settings
        distrib = asbool(request.params.get('distrib', 'false'))
        istrib = asbool(request.params.get('distrib', 'false'))
        self.latest = asbool(request.params.get('latest', 'true'))
        if self.latest is False:
            self.latest = None  # all versions
        self.replica = asbool(request.params.get('replica', 'false'))
        if self.replica is True:
            self.replica = None  # master + replica
        self.conn = SearchConnection(settings.get('esgfsearch.url'), distrib=distrib)

    def search_files(self):
        dataset_id = self.request.params.get(
            'dataset_id',
            'cmip5.output1.MPI-M.MPI-ESM-LR.1pctCO2.day.atmos.cfDay.r1i1p1.v20120314|esgf1.dkrz.de')
        ctx = self.conn.new_context(search_type=TYPE_FILE, latest=self.latest, replica=self.replica)
        ctx = ctx.constrain(dataset_id=dataset_id)
        paged_results = []
        for result in ctx.search():
            paged_results.append(dict(
                filename=result.filename,
                download_url=result.download_url,
                opendap_url=result.opendap_url,
            ))
        return dict(files=paged_results)

    def view(self):
        if 'start' in self.request.params and 'end' in self.request.params:
            temporal = 'true'
        else:
            temporal = 'false'
        result = dict(
            query=self.request.params.get('query', ''),
            selected=self.request.params.get('selected', 'project'),
            distrib=self.request.params.get('distrib', 'false'),
            replica=self.request.params.get('replica', 'false'),
            latest=self.request.params.get('latest', 'true'),
            temporal=temporal,
            start=self.request.params.get('start', '2001'),
            end=self.request.params.get('end', '2005'),
            constraints=self.request.params.get('constraints', ''),
        )
        result.update(search(self.request))
        result['form'] = Form(ESGFSearchSchema())
        result['quickview'] = True
        result['page'] = 0
        return result
