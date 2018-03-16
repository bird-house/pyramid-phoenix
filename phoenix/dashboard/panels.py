from datetime import datetime, timedelta
from pyramid_layout.panel import panel_config

from phoenix.security import Guest
from phoenix.catalog import WPS_TYPE, THREDDS_TYPE

import logging
logger = logging.getLogger(__name__)


@panel_config(name='dashboard_overview', renderer='templates/dashboard/panels/overview.pt')
def dashboard_overview(context, request):
    return dict(people=request.db.users.count(),
                jobs=request.db.jobs.count(),
                wps=len(request.catalog.get_services(service_type=WPS_TYPE)),
                tds=len(request.catalog.get_services(service_type=THREDDS_TYPE)))


@panel_config(name='dashboard_people', renderer='templates/dashboard/panels/people.pt')
def dashboard_people(context, request):
    stats = dict(total=request.db.users.count())
    stats['not_activated'] = request.db.users.find({"group": Guest}).count()

    d = datetime.now() - timedelta(hours=24)
    stats['logged_in_today'] = request.db.users.find({"last_login": {"$gt": d}}).count()

    d = datetime.now() - timedelta(days=7)
    stats['logged_in_this_week'] = request.db.users.find({"last_login": {"$gt": d}}).count()
    return stats


@panel_config(name='dashboard_jobs', renderer='templates/dashboard/panels/jobs.pt')
def dashboard_jobs(context, request):
    return dict(total=request.db.jobs.count(),
                running=request.db.jobs.find(
                {"status": {'$in': ['ProcessAccepted', 'ProcessPaused', 'ProcessStarted']}}).count(),
                failed=request.db.jobs.find({"status": "ProcessFailed"}).count(),
                succeeded=request.db.jobs.find({"status": "ProcessSucceeded"}).count())
