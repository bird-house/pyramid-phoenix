from pyramid_layout.panel import panel_config
from phoenix import models

import logging
logger = logging.getLogger(__name__)

@panel_config(name='dashboard_users', renderer='phoenix:templates/panels/dashboard_users.pt')
def dashboard_users(context, request):
    from phoenix.models import user_stats
    return user_stats(request)

@panel_config(name='dashboard_jobs', renderer='phoenix:templates/panels/dashboard_jobs.pt')
def dashboard_jobs(context, request):
    return dict(total = request.db.jobs.count(),
                started = request.db.jobs.find({"is_complete": False}).count(),
                failed = request.db.jobs.find({"is_complete": True, "is_succeded": False}).count(),
                succeded = request.db.jobs.find({"is_succeded": True}).count())
