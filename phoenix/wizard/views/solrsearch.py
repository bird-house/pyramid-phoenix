from pyramid.view import view_config

from phoenix.wizard.views import Wizard
import pysolr


import logging
logger = logging.getLogger(__name__)

import colander
import deform
class Schema(colander.MappingSchema):
    url = colander.SchemaNode(
        colander.String(),
        missing = '',
        default = '',
        widget = deform.widget.HiddenWidget()
        )

class SolrSearch(Wizard):
    def __init__(self, request):
        super(SolrSearch, self).__init__(request, name='wizard_solr', title="Solr Search")

    def breadcrumbs(self):
        breadcrumbs = super(SolrSearch, self).breadcrumbs()
        breadcrumbs.append(dict(route_path=self.request.route_path(self.name), title=self.title))
        return breadcrumbs

    def schema(self):
        return Schema()

    def next_success(self, appstruct):
        self.success(appstruct)
        return self.next('wizard_done')

    def custom_view(self):
        query = self.request.params.get('q', '')
        page = int(self.request.params.get('page', '0'))
        category = self.request.params.get('category')
        source = self.request.params.get('source')
        rows = 10
        start = page * rows
        solr_query = query
        if len(solr_query.strip()) == 0:
            solr_query = '*:*'
        try:
            solr = pysolr.Solr('http://localhost:8983/solr/birdhouse/', timeout=10)
            options = {'start':start, 'rows':rows, 'facet':'true', 'facet.field':['category', 'source']}
            if category or source:
                options['fq'] = []
                if category:
                    options['fq'].append('category:{0}'.format(category))
                if source:
                    options['fq'].append( 'source:{0}'.format(source))
            logger.debug('solr options %s', options)
            results = solr.search(solr_query, **options)
            sources = results.facets['facet_fields']['source'][::2]
            hits = results.hits
        except:
            logger.exception("solr search failed")
            self.session.flash("Solr service is not available.", queue='danger')
            results = []
            sources = []
            hits = 0
        end = min(hits, ((page + 1) * rows))
        return dict(results=results, query=query, category=category, sources=sources, hits=hits, start=start+1, end=end, page=page)

    @view_config(route_name='wizard_solr', renderer='../templates/wizard/solrsearch.pt')
    def view(self):
        return super(SolrSearch, self).view()
