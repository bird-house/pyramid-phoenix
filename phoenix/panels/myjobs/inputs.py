from pyramid_layout.panel import panel_config

import logging
logger = logging.getLogger(__name__)

class Inputs(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.session = self.request.session
    
    @panel_config(name='myjobs_inputs', renderer='phoenix:templates/panels/myjobs_default.pt')
    def panel(self):
        jobid = self.session.get('jobid')

        items = []
        from phoenix.grid import MyGrid
        grid = MyGrid(
            self.request,
            items,
            ['input', 'value', ''])
        return dict(grid=grid)
