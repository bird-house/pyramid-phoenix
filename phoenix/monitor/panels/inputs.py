from pyramid_layout.panel import panel_config

from phoenix.wps import check_status

import logging
LOGGER = logging.getLogger(__name__)


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

    @panel_config(name='monitor_inputs', renderer='../templates/monitor/panels/media.pt')
    def panel(self):
        job_id = self.request.matchdict.get('job_id')
        wps_output_url = self.request.registry.settings.get('wps.output.url')

        items = []
        for inp in process_inputs(self.request, job_id):
            dataset = None
            proxy_reference = inp.reference
            # TODO: use config for nwms dynamic services
            if self.request.map_activated and inp.mimeType and 'netcdf' in inp.mimeType and inp.reference:
                if 'cache' in inp.reference:
                    dataset = "cache" + inp.reference.split('cache')[1]
                elif 'wpsoutputs' in inp.reference:
                    dataset = "outputs" + inp.reference.split('wpsoutputs')[1]
                elif 'download' in inp.reference:
                    dataset = "uploads" + inp.reference.split('download')[1]
                elif 'CMIP5/data' in inp.reference:
                    dataset = "archive-cmip5" + inp.reference.split('CMIP5/data')[1]
                elif 'CORDEX/data' in inp.reference:
                    dataset = "archive-cordex" + inp.reference.split('CORDEX/data')[1]
                elif 'OBS4MIPS/data' in inp.reference:
                    dataset = "archive-obs4mips" + inp.reference.split('OBS4MIPS/data')[1]
            if inp.reference and wps_output_url and inp.reference.startswith(wps_output_url):
                proxy_reference = self.request.route_url(
                    'download_wpsoutputs',
                    subpath=inp.reference.split(wps_output_url)[1])
                LOGGER.debug("proxy reference: %s", proxy_reference)
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
                              proxy_reference=proxy_reference,
                              dataset=dataset,
                              category=category))

        items = sorted(items, key=lambda item: item['identifier'], reverse=1)
        return dict(items=items)
