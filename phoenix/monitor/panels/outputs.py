from pyramid_layout.panel import panel_config

from phoenix.wps import check_status

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
        if job.get('is_workflow', False):
            outputs = collect_outputs(status_location=job.get('worker_status_location'))
        else:
            outputs = collect_outputs(status_location=job.get('status_location'), response=job.get('response'))
    return outputs


class Outputs(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.session = self.request.session

    @panel_config(name='job_outputs', renderer='../templates/monitor/panels/media.pt')
    def panel(self):
        job_id = self.request.matchdict.get('job_id')
        wps_output_url = self.request.registry.settings.get('wps.output.url')

        items = []
        for output in process_outputs(self.request, job_id).values():
            dataset = None
            proxy_reference = output.reference
            LOGGER.debug("output reference: %s", output.reference)
            if output.reference and 'wpsoutputs' in output.reference:
                if self.request.map_activated and output.mimeType and 'netcdf' in output.mimeType:
                    dataset = "outputs" + output.reference.split('wpsoutputs')[1]
                if wps_output_url and output.reference.startswith(wps_output_url):
                    proxy_reference = self.request.route_url(
                        'download_wpsoutputs',
                        subpath=output.reference.split(wps_output_url)[1])
                    LOGGER.debug("proxy reference: %s", proxy_reference)
            if output.mimeType:
                category = 'ComplexType'
                data = output.data
            elif output.dataType == 'BoundingBoxData':
                category = 'BoundingBoxType'
                data = ["{0.minx},{0.miny},{0.maxx},{0.maxy}".format(bbox) for bbox in output.data]
            else:
                category = 'LiteralType'
                data = output.data

            LOGGER.debug("proxy_reference: %s", proxy_reference)

            items.append(dict(title=output.title,
                              abstract=output.abstract,
                              identifier=output.identifier,
                              mime_type=output.mimeType,
                              data=data,
                              reference=output.reference,
                              proxy_reference=proxy_reference,
                              dataset=dataset,
                              category=category))
        items = sorted(items, key=lambda item: item['identifier'], reverse=1)
        return dict(items=items)
