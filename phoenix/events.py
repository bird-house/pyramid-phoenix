class JobStarted(object):
    def __init__(self, request, task_id):
        self.request = request
        self.task_id = task_id


class JobFinished(object):
    def __init__(self, job):
        self.job = job

    def succeeded(self):
        return self.job.get('status') == "ProcessSucceeded"


class SettingsChanged(object):
    def __init__(self, request, new_settings):
        self.request = request
        self.new_settings = new_settings

    def converted_settings(self):
        converted = {}
        for key, value in self.new_settings.iteritems():
            converted[key.replace('_', '.')] = value
        return converted
