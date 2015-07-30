from pyramid.view import view_config

from phoenix.wizard.views import Wizard
import pysolr


import logging
logger = logging.getLogger(__name__)

import colander
import deform
class Schema(colander.MappingSchema):
    query = colander.SchemaNode(
        colander.String(),
        missing = '',
        default = '',
        widget = deform.widget.HiddenWidget())
    category = colander.SchemaNode(
        colander.String(),
        missing = '',
        default = '',
        widget = deform.widget.HiddenWidget())
    source = colander.SchemaNode(
        colander.String(),
        missing = '',
        default = '',
        widget = deform.widget.HiddenWidget())

    
class SolrSearch(Wizard):
    def __init__(self, request):
        super(SolrSearch, self).__init__(request, name='wizard_solr', title="Solr Search")

    def breadcrumbs(self):
        breadcrumbs = super(SolrSearch, self).breadcrumbs()
        breadcrumbs.append(dict(route_path=self.request.route_path(self.name), title=self.title))
        return breadcrumbs

    def schema(self):
        return Schema()

    def appstruct(self):
        appstruct = super(SolrSearch, self).appstruct()
        appstruct['query'] = self.request.params.get('q', colander.null)
        appstruct['category'] = self.request.params.get('category', colander.null)
        appstruct['source'] = self.request.params.get('source', colander.null)
        return appstruct

    def next_success(self, appstruct):
        self.success(appstruct)
        return self.next('wizard_done')

    def custom_view(self):
        query = self.request.params.get('q', '')
        page = int(self.request.params.get('page', '0'))
        category = self.request.params.get('category')
        source = self.request.params.get('source')
        tag = self.request.params.get('tag')
        rows = 10
        start = page * rows
        solr_query = query
        if len(solr_query.strip()) == 0:
            solr_query = '*:*'
        try:
            url = self.request.registry.settings.get('solr.url')
            solr = pysolr.Solr(url, timeout=10)
            options = {'start':start, 'rows':rows,
                       'facet':'true', 'facet.field':['category', 'source', 'tags'],
                       'facet.limit': 300, 'facet.mincount': 1}
            if tag or category or source:
                options['fq'] = []
                if category:
                    options['fq'].append('category:{0}'.format(category))
                if source:
                    options['fq'].append('source:{0}'.format(source))
                if tag:
                    options['fq'].append('tags:{0}'.format(tag))
            results = solr.search(solr_query, **options)
            sources = results.facets['facet_fields']['source'][::2]
            tag_values = results.facets['facet_fields']['tags'][::2]
            tag_counts = results.facets['facet_fields']['tags'][1::2]
            tags = []
            for i in xrange(0, len(tag_counts)):
                if tag_counts[i] == results.hits:
                    # each dataset has the same tag
                    continue
                tags.append(tag_values[i])
            hits = results.hits
        except:
            logger.exception("solr search failed")
            self.session.flash("Solr service is not available.", queue='danger')
            results = []
            sources = []
            tags = []
            hits = 0
        end = min(hits, ((page + 1) * rows))
        return dict(results=results, query=query, category=category, sources=sources, tags=tags, selected_source=source, hits=hits, start=start+1, end=end, page=page)

    @view_config(route_name='wizard_solr', renderer='../templates/wizard/solrsearch.pt')
    def view(self):
        return super(SolrSearch, self).view()
