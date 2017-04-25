from pyramid.view import view_config, view_defaults

from phoenix.views import MyView
from phoenix.wps import check_status

import logging
LOGGER = logging.getLogger(__name__)


@view_defaults(permission='view', layout='default')
class JobStatus(MyView):
    def __init__(self, request):
        self.request = request
        self.job_id = self.request.matchdict.get('job_id')
        self.collection = self.request.db.jobs
        super(JobStatus, self).__init__(request, name='job_status', title='')

    @view_config(route_name='job_status', renderer='../templates/monitor/status.pt')
    def view(self):
        status = 'ProcessAccepted'
        log = None
        # is job running?
        if self.collection.find({"task_id": self.job_id}).count() == 1:
            job = self.collection.find_one({"task_id": self.job_id})
            progress = job.get('progress', 0)
            status = job['status']
            log = job.get('log', ['No status message'])
            if status == 'ProcessSucceeded':
                execution = check_status(job['status_location'], verify=False)
                for output in execution.processOutputs:
                    if output.identifier == 'output':
                        break
                if output.reference:
                    result = '<a href="{0}" class="btn btn-success btn-xs" target="_blank">Show Output</a>'.format(
                        output.reference)
                else:
                    result = '{0}'.format(', '.join(output.data))
                msg = '<h4>Job Succeeded: {1} <a href="{0}" class="btn btn-info btn-xs"> Details</a></h4>'
                url = self.request.route_path('job_details', tab='outputs', job_id=self.job_id)
                self.session.flash(msg.format(url, result), queue="success")
            elif status == 'ProcessFailed':
                msg = '<h4>Job Failed [{0}/100]</h4>'
                self.session.flash(msg.format(progress), queue="danger")
            else:
                msg = '<h4><img src="/static/phoenix/img/ajax-loader.gif"></img> Job Running [{0}/100]</h4>'  # noqa
                self.session.flash(msg.format(progress), queue="warning")
        return dict(status=status, log=log)
