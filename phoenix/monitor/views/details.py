from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPException, HTTPFound, HTTPNotFound
from pyramid.security import authenticated_userid
from . import Monitor
from .. panels.outputs import process_outputs

import logging
logger = logging.getLogger(__name__)

class Details(Monitor):
    def __init__(self, request):
        super(Details, self).__init__(
            request, name='monitor_details', title='Details')

    def breadcrumbs(self):
        breadcrumbs = super(Details, self).breadcrumbs()
        breadcrumbs.append(dict(route_path='', title=self.title))
        return breadcrumbs
        
    @view_config(renderer='json', name='publish.output')
    def publish(self):
        import uuid
        outputid = self.request.params.get('outputid')
        # TODO: why use session for jobid?
        jobid = self.session.get('jobid')
        result = dict()
        if outputid is not None:
            output = process_outputs(self.request, jobid).get(outputid)

            result = dict(
                identifier = uuid.uuid4().get_urn(),
                title = output.title,
                abstract = getattr(output, "abstract", ""),
                creator = authenticated_userid(self.request),
                source = output.reference,
                format = output.mimeType,
                keywords = 'one,two,three')
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
                format = output.mimeType)
        return result

    @view_config(route_name='monitor_details', renderer='../templates/monitor/details.pt')
    def view(self):
        tab = self.request.matchdict.get('tab')
        # TODO: this is a bit fishy ...
        jobid = self.request.matchdict.get('jobid')
        if jobid is not None:
            self.session['jobid'] = jobid
            self.session.changed()

        lm = self.request.layout_manager
        if tab == 'log':
            lm.layout.add_heading('monitor_log')
        else:
            lm.layout.add_heading('monitor_outputs')

        return dict(active=tab, jobid=jobid)

        


