from pyramid_layout.panel import panel_config

import logging
logger = logging.getLogger(__name__)

class Workflow(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.session = self.request.session
     
    @panel_config(name='myjobs_workflow', renderer='phoenix:templates/panels/myjobs_default.pt')
    def panel(self):
        jobid = self.session.get('jobid')
        
        items = []
        from phoenix.models import process_outputs
        for oid,output in process_outputs(self.request, jobid, tab='workflow').items():
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

        return dict(grid=grid)

