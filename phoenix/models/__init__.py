from pyramid.security import authenticated_userid

import uuid
from datetime import datetime, timedelta

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




    





