from pyramid.settings import asbool

from pyesgf.search import SearchConnection

import logging
LOGGER = logging.getLogger(__name__)


class Actions(object):
    def __init__(self, request):
        self.request = request
        self.session = request.session
        self.settings = self.request.registry.settings

    def search(self):
        selected = self.request.params.get('selected', 'project')
        limit = int(self.request.params.get('limit', '0'))
        distrib = asbool(self.request.params.get('distrib', 'false'))
        latest = asbool(self.request.params.get('latest', 'true'))
        if latest is False:
            latest = None  # all versions
        replica = asbool(self.request.params.get('replica', 'false'))
        if replica is True:
            replica = None  # master + replica

        constraints = dict()
        if 'constraints' in self.request.params:
            for constrain in self.request.params['constraints'].split(','):
                if constrain.strip():
                    key, value = constrain.split(':', 1)
                    constraints[key] = value

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
        ctx = conn.new_context(facets=','.join(facets), latest=latest, replica=replica)
        LOGGER.debug("latest=%s, replica=%s", latest, replica)
        ctx = ctx.constrain(**constraints)
        if 'start' in self.request.params and 'end' in self.request.params:
            ctx = ctx.constrain(from_timestamp=self.request.params['start'], to_timestamp=self.request.params['end'])
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
