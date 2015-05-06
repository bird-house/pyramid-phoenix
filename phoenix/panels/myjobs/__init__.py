from pyramid_layout.panel import panel_config

import logging
logger = logging.getLogger(__name__)

@panel_config(name='myjobs_log', renderer='phoenix:templates/panels/myjobs_log.pt')
def myjobs_log(context, request):
    return {}
