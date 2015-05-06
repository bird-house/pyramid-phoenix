from pyramid.view import view_config, view_defaults

from pyramid.httpexceptions import HTTPException, HTTPFound, HTTPNotFound

from phoenix.models import process_outputs
from phoenix.views.myjobs import MyJobs

import logging
logger = logging.getLogger(__name__)

@view_defaults(permission='edit', layout='default')
class JobDetails(MyJobs):
    def __init__(self, request):
        super(JobDetails, self).__init__(
            request, name='myjobs_details', title='Job Details')
        
    @view_config(renderer='json', name='publish.output')
    def publish(self):
        import uuid
        outputid = self.request.params.get('outputid')
        # TODO: why use session for jobid?
        jobid = self.session.get('jobid')
        result = dict()
        if outputid is not None:
            output = process_outputs(self.request, jobid).get(outputid)

            # TODO: how about schema.bind?
            result = dict(
                identifier = uuid.uuid4().get_urn(),
                title = output.title,
                abstract = getattr(output, "abstract", ""),
                creator = self.user_email(),
                source = output.reference,
                format = output.mimeType,
                keywords = 'one,two,three',
                )

        return result

    @view_config(renderer='json', name='upload.output')
    def upload(self):
        outputid = self.request.params.get('outputid')
        # TODO: why use session for jobid?
        jobid = self.session.get('jobid')
        result = dict()
        if outputid is not None:
            output = process_outputs(self.request, jobid).get(outputid)
            user = self.get_user()

            result = dict(
                username = user.get('swift_username'),
                container = 'WPS Outputs',
                prefix = jobid,
                source = output.reference,
                format = output.mimeType,
                )

        return result

    @view_config(route_name='myjobs_details', renderer='phoenix:templates/myjobs/details.pt')
    def view(self):
        tab = self.request.matchdict.get('tab')
        # TODO: this is a bit fishy ...
        jobid = self.request.matchdict.get('jobid')
        if jobid is not None:
            self.session['jobid'] = jobid
            self.session.changed()

        lm = self.request.layout_manager
        if tab == 'log':
            lm.layout.add_heading('myjobs_log')
        else:
            lm.layout.add_heading('myjobs_outputs')

        return dict(active=tab, jobid=jobid)

        


