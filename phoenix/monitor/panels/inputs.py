from pyramid_layout.panel import panel_config

import logging
logger = logging.getLogger(__name__)


def collect_inputs(status_location):
    from owslib.wps import WPSExecution
    execution = WPSExecution()
    execution.checkStatus(url=status_location, sleepSecs=0)
    return execution.dataInputs


def process_inputs(request, job_id):
    job = request.db.jobs.find_one({'identifier': job_id})
    inputs = {}
    if job and job.get('status') == 'ProcessSucceeded':
        if job.get('is_workflow', False):
            inputs = collect_inputs(job['worker_status_location'])
        else:
            inputs = collect_inputs(job['status_location'])
    return inputs


class Inputs(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.session = self.request.session
    
    @panel_config(name='monitor_inputs', renderer='../templates/monitor/panels/media.pt')
    def panel(self):
        job_id = self.request.matchdict.get('job_id')
        
        items = []
        for inp in process_inputs(self.request, job_id):
            dataset = None
            if self.request.wms_activated and inp.mimeType and 'netcdf' in inp.mimeType:
                if inp.reference and 'cache' in inp.reference:
                    dataset = "cache" + inp.reference.split('cache')[1]
                elif inp.reference and 'wpsoutputs' in inp.reference:
                    dataset = "outputs" + inp.reference.split('wpsoutputs')[1]
                elif inp.reference and 'download' in inp.reference:
                    dataset = "uploads" + inp.reference.split('download')[1]
            if inp.mimeType:
                category = 'ComplexType'
            else:
                category = 'LiteralType'

            items.append(dict(title=inp.title,
                              abstract=inp.abstract,
                              identifier=inp.identifier,
                              mime_type=inp.mimeType,
                              data=inp.data,
                              reference=inp.reference,
                              dataset=dataset,
                              category=category))

        items = sorted(items, key=lambda item: item['identifier'], reverse=1)
        return dict(items=items)





