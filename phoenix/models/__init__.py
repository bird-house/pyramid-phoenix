from pyramid.security import authenticated_userid

import uuid
from datetime import datetime, timedelta
import pymongo
from phoenix.utils import localize_datetime
from dateutil import parser as datetime_parser

from phoenix import utils
from phoenix.security import Guest

import logging
logger = logging.getLogger(__name__)

def mongodb(registry):
    settings = registry.settings
    return pymongo.Connection(settings['mongodb.url'])[settings['mongodb.db_name']]

def get_user(request, email=None):
    if email is None:
        email = authenticated_userid(request)
    return request.db.users.find_one(dict(email=email))

def add_user(
    request,
    email,
    openid='',
    name='unknown',
    organisation='unknown',
    notes='',
    group=Guest):
    user=dict(
        identifier = uuid.uuid4().get_urn(),
        email = email,
        openid = openid,
        name = name,
        organisation = organisation,
        notes = notes,
        group = group,
        creation_time = datetime.now(),
        last_login = datetime.now())
    request.db.users.save(user)
    return request.db.users.find_one({'email':email})

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

def user_cert_valid(request, valid_hours=8):
    cert_expires = get_user(request).get('cert_expires')
    if cert_expires != None:
        timestamp = datetime_parser.parse(cert_expires)
        now = localize_datetime(datetime.utcnow())
        valid_hours = timedelta(hours=valid_hours)
        # cert must be valid for some hours
        if timestamp > now + valid_hours:
            return True
    return False

def get_wps_list(request):
    csw = request.csw
    from owslib.fes import PropertyIsEqualTo
    wps_query = PropertyIsEqualTo('dc:format', 'WPS')
    csw.getrecords2(constraints=[wps_query], maxrecords=20)
    return csw.records.values()





