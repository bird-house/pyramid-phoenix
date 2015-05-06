from pyramid_layout.panel import panel_config

import logging
logger = logging.getLogger(__name__)

@panel_config(name='myjobs_details', renderer='phoenix:templates/panels/myjobs_details.pt')
def details(context, request):
    jobid = request.session.get('jobid')
    from phoenix.models import job_details
    return dict(job=job_details(request, jobid=jobid))

@panel_config(name='myjobs_log', renderer='phoenix:templates/panels/myjobs_log.pt')
def log(context, request):
    return {}
