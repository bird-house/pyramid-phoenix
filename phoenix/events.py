class JobStarted(object):
    def __init__(self, request, task_id):
        self.request = request
        self.task_id = task_id

class JobFinished(object):
    def __init__(self, job):
        self.job = job
        
    def succeeded(self):
        return self.job.get('status') == "ProcessSucceeded"
