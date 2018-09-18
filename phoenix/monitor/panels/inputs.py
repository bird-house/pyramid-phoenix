from pyramid_layout.panel import panel_config

from phoenix.wps import check_status
from phoenix.monitor.utils import escape_output

import logging
LOGGER = logging.getLogger("PHOENIX")


def collect_inputs(status_location=None, response=None):
    execution = check_status(url=status_location, response=response, sleep_secs=0)
    return execution.dataInputs


def process_inputs(request, job_id):
    job = request.db.jobs.find_one({'identifier': job_id})
    inputs = {}
    if job and job.get('status') == 'ProcessSucceeded':
        if job.get('is_workflow', False):
            inputs = collect_inputs(status_location=job.get('worker_status_location'))
        else:
            inputs = collect_inputs(status_location=job.get('status_location'), response=job.get('response'))
    return inputs


class Inputs(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.session = self.request.session

    @panel_config(name='job_inputs', renderer='../templates/monitor/panels/media.pt')
    def panel(self):
        job_id = self.request.matchdict.get('job_id')

        items = []
        for inp in process_inputs(self.request, job_id):
            if inp.mimeType:
                category = 'ComplexType'
                data = inp.data
            elif inp.dataType == 'BoundingBoxData':
                category = 'BoundingBoxType'
                data = ["{0.minx},{0.miny},{0.maxx},{0.maxy}".format(bbox) for bbox in inp.data]
            elif inp.identifier == 'password':
                data = "********"
            else:
                category = 'LiteralType'
                data = inp.data

            items.append(dict(title=inp.title,
                              abstract=inp.abstract,
                              identifier=inp.identifier,
                              mime_type=inp.mimeType,
                              data=escape_output(data),
                              reference=escape_output(inp.reference),
                              category=category))

        items = sorted(items, key=lambda item: item['identifier'], reverse=1)
        return dict(items=items)
