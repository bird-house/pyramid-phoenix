from pyramid_layout.panel import panel_config

from phoenix.grid import CustomGrid

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
    if job is not None and job.get('is_succeded', False):
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

    @panel_config(name='monitor_outputs', renderer='../templates/panels/monitor_outputs.pt')
    def panel(self):
        job_id = self.session.get('job_id')

        items = []
        for output in process_outputs(self.request, job_id).values():
            items.append(dict(title=output.title,
                              abstract=output.abstract,
                              identifier=output.identifier,
                              mime_type=output.mimeType,
                              data=output.data,
                              reference=output.reference))
        items = sorted(items, key=lambda item: item['identifier'], reverse=1)

        grid = ProcessOutputsGrid(
                self.request,
                items,
                ['output', 'value', ''],
            )

        return dict(grid=grid)


class ProcessOutputsGrid(CustomGrid):
    def __init__(self, request, *args, **kwargs):
        super(ProcessOutputsGrid, self).__init__(request, *args, **kwargs)
        self.column_formats['output'] = self.output_td
        self.column_formats['value'] = self.value_td
        # self.column_formats['preview'] = self.preview_td
        self.column_formats[''] = self.buttongroup_td
        self.exclude_ordering = self.columns

    def output_td(self, col_num, i, item):
        return self.render_title_td(
            title=item.get('title'), 
            abstract=item.get('abstract'))

    def value_td(self, col_num, i, item):
        return self.render_td(renderer="value_td.mako",
                data=item.get('data', []),
                format=item.get('mime_type'),
                source=item.get('reference'))

    def preview_td(self, col_num, i, item):
        return self.render_preview_td(format=item.get('mime_type'), source=item.get('reference'))

    def buttongroup_td(self, col_num, i, item):
        from phoenix.utils import ActionButton
        buttons = []
        if item.get('reference') is not None:
            buttons.append( ActionButton('view', title=u'Download', icon="fa fa-download",
                                         href=item.get('reference', "#"), new_window=True))
            if self.request.wms_activated and 'netcdf' in item.get('mime_type'):
                if 'wpsoutputs' in item.get('reference'):
                    dataset = "outputs" + item.get('reference').split('wpsoutputs')[1]
                    buttons.append( ActionButton("mapit", title=u'Show on Map', icon="fa fa-map-marker",
                                    href=self.request.route_path('map', _query=[('dataset', dataset)])))
            buttons.append(ActionButton('add_to_cart', title=u'Add to Cart', icon="fa fa-cart-plus",
                                        href=item.get('reference', "#"), new_window=True))
        return self.render_buttongroup_td(buttons=buttons)
        



