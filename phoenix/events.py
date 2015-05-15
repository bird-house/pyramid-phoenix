class JobFinished(object):
    def __init__(self, job, success=False):
        self.job = job
        self.success = success
