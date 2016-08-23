from pyramid_layout.panel import panel_config

import logging
logger = logging.getLogger(__name__)


def collect_outputs(status_location):
    from owslib.wps import WPSExecution
    execution = WPSExecution()
    execution.checkStatus(url=status_location, sleepSecs=0)
    outputs = {}
    for output in execution.processOutputs:
        outputs[output.identifier] = output
    return outputs


def process_outputs(request, job_id):
    job = request.db.jobs.find_one({'identifier': job_id})
    outputs = {}
    if job and job.get('status') == 'ProcessSucceeded':
        if job.get('is_workflow', False):
            outputs = collect_outputs(job['worker_status_location'])
        else:
            outputs = collect_outputs(job['status_location'])
    return outputs


class Outputs(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.session = self.request.session

    @panel_config(name='monitor_outputs', renderer='../templates/monitor/panels/media.pt')
    def panel(self):
        job_id = self.request.matchdict.get('job_id')

        items = []
        for output in process_outputs(self.request, job_id).values():
            dataset = None
            if self.request.wms_activated and output.mimeType and 'netcdf' in output.mimeType:
                if output.reference and 'wpsoutputs' in output.reference:
                    dataset = "outputs" + output.reference.split('wpsoutputs')[1]
            if output.mimeType:
                category = 'ComplexType'
            else:
                category = 'LiteralType'

            items.append(dict(title=output.title,
                              abstract=output.abstract,
                              identifier=output.identifier,
                              mime_type=output.mimeType,
                              data=output.data,
                              reference=output.reference,
                              dataset=dataset,
                              category=category))
        items = sorted(items, key=lambda item: item['identifier'], reverse=1)
        return dict(items=items)

        



