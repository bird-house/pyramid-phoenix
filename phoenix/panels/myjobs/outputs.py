from pyramid_layout.panel import panel_config

import logging
logger = logging.getLogger(__name__)

class MyJobsOutputs(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @panel_config(name='myjobs_outputs', renderer='phoenix:templates/panels/myjobs_outputs.pt')
    def panel(self):
        return {}
