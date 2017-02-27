from pyesgf.search import SearchConnection

import logging
LOGGER = logging.getLogger(__name__)


class Actions(object):
    def __init__(self, request):
        self.request = request
        self.session = request.session

    def search(self):
        LOGGER.debug(self.request.params.keys)
        conn = SearchConnection('https://esgf-data.dkrz.de/esg-search', distrib=False)
        ctx = conn.new_context(project='CMIP5', query='humidity')
        return {}
