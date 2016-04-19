from pyramid.security import authenticated_userid

import uuid
from datetime import datetime, timedelta

from phoenix.security import Guest

import logging
logger = logging.getLogger(__name__)

def get_user(request):
    userid = authenticated_userid(request)
    return request.db.users.find_one(dict(identifier=userid))





    





