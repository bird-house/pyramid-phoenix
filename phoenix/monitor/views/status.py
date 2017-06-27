from pyramid.view import view_config, view_defaults

from phoenix.views import MyView
from phoenix.wps import check_status
from phoenix.monitor.utils import output_details


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
        if self.collection.find({"identifier": self.job_id}).count() == 1:
            job = self.collection.find_one({"identifier": self.job_id})
            progress = job.get('progress', 0)
            status = job['status']
            log = job.get('log', ['No status message'])
            if status == 'ProcessSucceeded':
                execution = check_status(job['status_location'], verify=False)
                for output in execution.processOutputs:
                    if output.identifier == 'output':
                        break
                details = output_details(self.request, output)
                if details.get('proxy_reference'):
                    result = '<a href="{0}" class="btn btn-success btn-xs" target="_blank">Show Output</a>'.format(
                        details['proxy_reference'])
                else:
                    result = '<strong>{0}</strong>'.format(', '.join(details.get('data', '')))
                msg = '<h4>Job Succeeded: {1} <a href="{0}" class="btn btn-info btn-xs"> Details</a></h4>'
                url = self.request.route_path('job_details', tab='outputs', job_id=self.job_id)
                self.session.flash(msg.format(url, result), queue="success")
            elif status == 'ProcessFailed':
                msg = '<h4>Job Failed [{0}/100]</h4>'
                self.session.flash(msg.format(progress), queue="danger")
            else:
                msg = '<h4><i class="fa fa-cog fa-spin text-muted fa-lg"></i> Job Running [{0}/100]</h4>'
                # msg = """
                # <div class="row">
                #     <div class="col-md-3"
                #         <h3>
                #             <i class="fa fa-cog fa-spin text-muted fa-lg"></i>
                #             Job Running
                #             <div class="progress" data-toggle="tooltip" title="Job progress.">
                #                 <div class="progress-bar progress-bar-striped active" role="progressbar"
                #                      aria-valuenow="{0}"
                #                      aria-valuemin="0" aria-valuemax="100" style="min-width: 2em; width: {0}%;">
                #                 <span>{0}% Complete</span>
                #             </div>
                #         </h3>
                #     </div>
                # </div>"""
                self.session.flash(msg.format(progress), queue="warning")
        return dict(status=status, log=log)
