from pyesgf.search import SearchConnection

import logging
LOGGER = logging.getLogger(__name__)


class Actions(object):
    def __init__(self, request):
        self.request = request
        self.session = request.session
        self.settings = self.request.registry.settings

    def search(self):
        if 'selected' in self.request.params:
            selected = self.request.params['selected']
        else:
            selected = 'project'

        constraints = dict()
        if 'constraints' in self.request.params:
            for constrain in self.request.params['constraints'].split(','):
                if constrain.strip():
                    key, value = constrain.split(':', 1)
                    constraints[key] = value

        if 'limit' in self.request.params:
            limit = int(self.request.params['limit'])
        else:
            limit = 0

        if 'distrib' in self.request.params:
            distrib = self.request.params['distrib'] == 'true'
        else:
            distrib = False

        if 'latest' in self.request.params:
            latest = self.request.params['latest'] == 'true'
        else:
            latest = True

        if 'replica' in self.request.params:
            replica = self.request.params['replica'] == 'true'
        else:
            replica = False

        facets = [
            "access",
            "cf_standard_name",
            "cmor_table",
            "data_node",
            "domain",
            "driving_model",
            "ensemble",
            "experiment",
            "institute",
            "model",
            "product",
            "project",
            "realm",
            "time_frequency",
            "variable",
            "variable_long_name",
            "version",
        ]

        conn = SearchConnection(self.settings.get('esgfsearch.url'), distrib=distrib)
        ctx = conn.new_context(latest=latest, facets=','.join(facets), replica=replica)
        ctx = ctx.constrain(**constraints)
        #return conn.send_search(query_dict=ctx._build_query(), limit=limit)
        #ctx.hit_count
        results = ctx.search(batch_size=10, ignore_facet_check=True)
        categories = [tag for tag in ctx.facet_counts if len(ctx.facet_counts[tag]) > 1]
        keywords = ctx.facet_counts[selected].keys()
        pinned_facets = []
        for facet in ctx.facet_counts:
            if len(ctx.facet_counts[facet]) == 1:
                pinned_facets.append("{}:{}".format(facet, ctx.facet_counts[facet].keys()[0]))
        return dict(
            numFound=ctx.hit_count,
            facets=categories,
            facetValues=keywords,
            pinnedFacets=pinned_facets)
