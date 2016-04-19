from pyramid.security import authenticated_userid

import uuid
from datetime import datetime, timedelta
from phoenix.utils import localize_datetime
from dateutil import parser as datetime_parser

from phoenix import utils
from phoenix.security import Guest

import logging
logger = logging.getLogger(__name__)

def get_user(request):
    userid = authenticated_userid(request)
    return request.db.users.find_one(dict(identifier=userid))

def add_user(
    request,
    login_id,
    email='',
    openid='',
    name='unknown',
    organisation='',
    notes='',
    group=Guest):
    user=dict(
        identifier =  str(uuid.uuid1()),
        login_id = login_id,
        email = email,
        openid = openid,
        name = name,
        organisation = organisation,
        notes = notes,
        group = group,
        creation_time = datetime.now(),
        last_login = datetime.now())
    request.db.users.save(user)
    return request.db.users.find_one({'identifier':user['identifier']})

def user_cert_valid(request, valid_hours=6):
    cert_expires = get_user(request).get('cert_expires')
    if cert_expires != None:
        timestamp = datetime_parser.parse(cert_expires)
        now = localize_datetime(datetime.utcnow())
        valid_hours = timedelta(hours=valid_hours)
        # cert must be valid for some hours
        if timestamp > now + valid_hours:
            return True
    return False


    





