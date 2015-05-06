from pyramid.view import view_config, view_defaults

from pyramid.httpexceptions import HTTPException, HTTPFound, HTTPNotFound

from phoenix.views.myjobs import MyJobs

import logging
logger = logging.getLogger(__name__)

@view_defaults(permission='edit', layout='default')
class JobDetails(MyJobs):
    def __init__(self, request):
        super(JobDetails, self).__init__(
            request, name='myjobs_details', title='Job Details')
        self.db = self.request.db


    def collect_outputs(self, status_location, prefix="job"):
        from owslib.wps import WPSExecution
        execution = WPSExecution()
        execution.checkStatus(url=status_location, sleepSecs=0)
        outputs = {}
        for output in execution.processOutputs:
            oid = "%s.%s" %(prefix, output.identifier)
            outputs[oid] = output
        return outputs

    def process_outputs(self, jobid, tab='outputs'):
        job = self.db.jobs.find_one({'identifier': jobid})
        outputs = self.collect_outputs(job['status_location'])
        # TODO: dirty hack for workflows ... not save and needs refactoring
        from owslib.wps import WPSExecution
        execution = WPSExecution()
        execution.checkStatus(url=job['status_location'], sleepSecs=0)
        if job['workflow']:
            import urllib
            import json
            wf_result_url = execution.processOutputs[0].reference
            wf_result_json = json.load(urllib.urlopen(wf_result_url))
            count = 0
            if tab == 'outputs':
                for url in wf_result_json.get('worker', []):
                    count = count + 1
                    outputs = self.collect_outputs(url, prefix='worker%d' % count )
            elif tab == 'resources':
                for url in wf_result_json.get('source', []):
                    count = count + 1
                    outputs = self.collect_outputs(url, prefix='source%d' % count )
            elif tab == 'inputs':
                outputs = {}
        else:
            if tab != 'outputs':
                outputs = {}
        return outputs
 
    @view_config(renderer='json', name='publish.output')
    def publish(self):
        import uuid
        outputid = self.request.params.get('outputid')
        # TODO: why use session for jobid?
        jobid = self.session.get('jobid')
        result = dict()
        if outputid is not None:
            output = self.process_outputs(jobid).get(outputid)

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
            output = self.process_outputs(jobid).get(outputid)
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

        items = []
        for oid,output in self.process_outputs(self.session.get('jobid'), tab).items():
            items.append(dict(title=output.title,
                              abstract=getattr(output, 'abstract', ""),
                              identifier=oid,
                              mime_type = output.mimeType,
                              data = output.data,
                              reference=output.reference))
        items = sorted(items, key=lambda item: item['identifier'], reverse=1)

        from phoenix.grid.processoutputs import ProcessOutputsGrid
        grid = ProcessOutputsGrid(
                self.request,
                items,
                ['output', 'value', ''],
            )
        return dict(active=tab, jobid=jobid, grid=grid, items=items)

        


