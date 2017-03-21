import logging
logger = logging.getLogger(__name__)


class Actions(object):
    def __init__(self, request):
        self.request = request
        self.session = request.session
