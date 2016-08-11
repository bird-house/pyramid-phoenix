import os
from pyramid.view import view_config, view_defaults

from mako.template import Template

from phoenix.views import MyView
import pysolr

import logging
logger = logging.getLogger(__name__)

solrsearch_script = Template(
    filename=os.path.join(os.path.dirname(__file__), "templates", "solrsearch", "solrsearch.js"),
    output_encoding="utf-8", input_encoding="utf-8")


@view_defaults(permission='view', layout='default')
class SolrSearch(MyView):
    def __init__(self, request):
        super(SolrSearch, self).__init__(request, name='solrsearch', title='Solrsearch')

    @view_config(route_name='solrsearch', renderer='templates/solrsearch/solrsearch.pt')
    def view(self):
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
            options = {'start': start, 'rows': rows,
                       'facet': 'true', 'facet.field': ['category', 'source', 'tags'],
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
        return dict(results=results, query=query, category=category, sources=sources, tags=tags, selected_source=source,
                    hits=hits, start=start+1, end=end, page=page,
                    solrsearch_script=solrsearch_script.render(request=self.request, query=query, page=page))


