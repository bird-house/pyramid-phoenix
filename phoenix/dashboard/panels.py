from datetime import datetime, timedelta
from pyramid_layout.panel import panel_config

from phoenix.security import Guest

import logging
logger = logging.getLogger(__name__)

def user_stats(request):
    num_unregistered = request.db.users.find({"group": Guest}).count()
    
    d = datetime.now() - timedelta(hours=3)
    num_logins_3h = request.db.users.find({"last_login": {"$gt": d}}).count()

    d = datetime.now() - timedelta(days=7)
    num_logins_7d = request.db.users.find({"last_login": {"$gt": d}}).count()

    return dict(num_users=request.db.users.count(),
                num_unregistered=num_unregistered,
                num_logins_3h=num_logins_3h,
                num_logins_7d=num_logins_7d)

@panel_config(name='dashboard_overview', renderer='templates/panels/dashboard_overview.pt')
def dashboard_overview(context, request):
    return dict()

@panel_config(name='dashboard_users', renderer='templates/panels/dashboard_users.pt')
def dashboard_users(context, request):
    return user_stats(request)

@panel_config(name='dashboard_jobs', renderer='templates/panels/dashboard_jobs.pt')
def dashboard_jobs(context, request):
    return dict(total = request.db.jobs.count(),
                started = request.db.jobs.find({"is_complete": False}).count(),
                failed = request.db.jobs.find({"is_complete": True, "is_succeded": False}).count(),
                succeded = request.db.jobs.find({"is_succeded": True}).count())
