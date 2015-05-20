class JobStarted(object):
    def __init__(self, request, task_id):
        self.request = request
        self.task_id = task_id

class JobFinished(object):
    def __init__(self, request, job):
        self.request = request
        self.job = job
        
    def succeded(self):
        return job.get('status') == "ProcessSuceeded"
