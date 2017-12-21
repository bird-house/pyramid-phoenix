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
        wps_output_url = self.request.registry.settings.get('wps.output.url')

        items = []
        for inp in process_inputs(self.request, job_id):
            wms_dataset_path = None
            proxy_reference = inp.reference
            # TODO: use config for nwms dynamic services
            if self.request.map_activated and inp.mimeType and 'netcdf' in inp.mimeType and inp.reference:
                if 'cache' in inp.reference:
                    wms_dataset_path = "cache" + inp.reference.split('cache')[1]
                elif 'wpsoutputs' in inp.reference:
                    wms_dataset_path = "outputs" + inp.reference.split('wpsoutputs')[1]
                elif 'download' in inp.reference:
                    wms_dataset_path = "uploads" + inp.reference.split('download')[1]
                elif 'CMIP5/data' in inp.reference:
                    wms_dataset_path = "archive-cmip5" + inp.reference.split('CMIP5/data')[1]
                elif 'CORDEX/data' in inp.reference:
                    wms_dataset_path = "archive-cordex" + inp.reference.split('CORDEX/data')[1]
                elif 'OBS4MIPS/data' in inp.reference:
                    wms_dataset_path = "archive-obs4mips" + inp.reference.split('OBS4MIPS/data')[1]
            if inp.reference and wps_output_url and inp.reference.startswith(wps_output_url):
                proxy_reference = self.request.route_url(
                    'download_wpsoutputs',
                    subpath=inp.reference.split(wps_output_url)[1])
                LOGGER.debug("proxy reference: %s", proxy_reference)
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
                              proxy_reference=escape_output(proxy_reference),
                              wms_dataset_path=escape_output(wms_dataset_path),
                              category=category))

        items = sorted(items, key=lambda item: item['identifier'], reverse=1)
        return dict(items=items)
