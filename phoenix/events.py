import logging
logger = logging.getLogger(__name__)

class JobFinished(object):
    def __init__(self, request, job, success=False):
        self.request = request
        self.job = job
        self.success = success
