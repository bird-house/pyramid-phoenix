from pyramid_layout.panel import panel_config
from pyramid.httpexceptions import HTTPFound

from phoenix.grid import CustomGrid

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
    if job is not None and job.get('is_succeded', False):
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
    
    @panel_config(name='monitor_inputs', renderer='../templates/panels/monitor_default.pt')
    def panel(self):
        job_id = self.session.get('job_id')
        
        items = []
        for inp in process_inputs(self.request, job_id):
            items.append(dict(title=inp.title,
                              abstract=inp.abstract,
                              identifier=inp.identifier,
                              mime_type=inp.mimeType,
                              data=inp.data,
                              reference=inp.reference))
        items = sorted(items, key=lambda item: item['identifier'], reverse=1)

        grid = ProcessInputsGrid(
                self.request,
                items,
                ['input', 'value', ''],
            )
        return dict(grid=grid)


class ProcessInputsGrid(CustomGrid):
    def __init__(self, request, *args, **kwargs):
        super(ProcessInputsGrid, self).__init__(request, *args, **kwargs)
        self.column_formats['input'] = self.input_td
        self.column_formats['value'] = self.value_td
        self.column_formats[''] = self.buttongroup_td
        self.exclude_ordering = self.columns

    def input_td(self, col_num, i, item):
        return self.render_title_td(
            title=item.get('title'), 
            abstract=item.get('abstract'))

    def value_td(self, col_num, i, item):
        return self.render_td(renderer="value_td.mako",
                data=item.get('data', []),
                format=item.get('mime_type'),
                source=item.get('reference'))

    def buttongroup_td(self, col_num, i, item):
        from phoenix.utils import ActionButton
        buttons = []
        if item.get('reference') is not None:
            buttons.append( ActionButton('view', title=u'Download', icon="fa fa-download",
                                         href=item.get('reference', "#"), new_window=True))
            if self.request.wms_activated and 'netcdf' in item.get('mime_type'):
                if 'cache' in item.get('reference'):
                    dataset = "cache" + item.get('reference').split('cache')[1]
                    buttons.append( ActionButton("mapit", title=u'Show on Map', icon="fa fa-map-marker",
                                    href=self.request.route_path('map', _query=[('dataset', dataset)])))
        return self.render_buttongroup_td(buttons=buttons)
    




