from dateutil import parser as datetime_parser
from datetime import timedelta
from datetime import datetime

from phoenix.utils import localize_datetime


def cert_ok(request, valid_hours=3):
    if not request.user:
        return False
    if request.user.get('esgf_token'):
        return True
    cert_expires = request.user.get('cert_expires')
    if cert_expires:
        timestamp = datetime_parser.parse(cert_expires)
        now = localize_datetime(datetime.utcnow())
        valid_hours = timedelta(hours=valid_hours)
        # cert must be valid for some hours
        if timestamp > now + valid_hours:
            return True
    return False
