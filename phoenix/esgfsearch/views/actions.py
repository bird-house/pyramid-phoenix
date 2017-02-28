from pyesgf.search import SearchConnection

import logging
LOGGER = logging.getLogger(__name__)


class Actions(object):
    def __init__(self, request):
        self.request = request
        self.session = request.session
        self.settings = self.request.registry.settings

    def search(self):
        query_dict = {}
        if 'limit' in self.request.params:
            limit = int(self.request.params['limit'])
        else:
            limit = 0

        if 'distrib' in self.request.params:
            distrib = self.request.params['distrib'] == 'true'
        else:
            distrib = False

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

        for param in self.request.params:
            if param in ['', 'limit', 'distrib', 'type', 'format', 'facets']:
                continue
            query_dict[param] = self.request.params[param]
        query_dict.update({'facets': ','.join(facets)})
        LOGGER.debug(query_dict)
        conn = SearchConnection(self.settings.get('esgfsearch.url'), distrib=distrib)
        return conn.send_search(query_dict, limit=limit)
