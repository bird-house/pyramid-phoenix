from pyramid_layout.panel import panel_config

from phoenix.wps import check_status
from phoenix.monitor.utils import output_details, output_details_from_metalink

import logging
LOGGER = logging.getLogger(__name__)


def collect_outputs(status_location=None, response=None):
    execution = check_status(url=status_location, response=response, sleep_secs=0)
    outputs = {}
    for output in execution.processOutputs:
        outputs[output.identifier] = output
    return outputs


def process_outputs(request, job_id):
    job = request.db.jobs.find_one({'identifier': job_id})
    outputs = {}
    if job and job.get('status') == 'ProcessSucceeded':
        outputs = collect_outputs(status_location=job.get('status_location'), response=job.get('response'))
    return outputs


class Outputs(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.session = self.request.session

    @panel_config(name='job_outputs', renderer='phoenix:monitor/templates/monitor/panels/media.pt')
    def panel(self):
        job_id = self.request.matchdict.get('job_id')
        items = []
        metalink_items = []
        for output in list(process_outputs(self.request, job_id).values()):
            items.append(output_details(self.request, output))

            if "application/metalink+xml" in output.mimeType:
                # If it is a metalink we need to resolve it and get the links to the files
                metalink_items.extend(output_details_from_metalink(output))

        items = sorted(items, key=lambda item: item['identifier'], reverse=1)
        metalink_items = sorted(metalink_items, key=lambda item: item['reference'], reverse=1)
        metalink_items.extend(items)
        return dict(items=metalink_items)
