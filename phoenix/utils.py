import os

import logging
logger = logging.getLogger(__name__)

SIGNIN_HTML = '<a class="navbar-link btn-lg" href="%s" data-toggle="tooltip" title="Sign in"><span class="fa fa-sign-in"></span></a>'
SIGNOUT_HTML = '<a class="navbar-link btn-lg" href="%s" data-toggle="tooltip" title="Sign out %s"><span class="fa fa-sign-out"></span></a>'

def button(request):
    """If the user is logged in, returns the logout button, otherwise returns the login button"""
    import markupsafe
    from pyramid.security import authenticated_userid
    if not authenticated_userid(request):
        return markupsafe.Markup(SIGNIN_HTML) % (request.route_path('account_login', protocol='oauth2'))
    else:
        return markupsafe.Markup(SIGNOUT_HTML) % (request.route_path('account_logout'), authenticated_userid(request))


def localize_datetime(dt, tz_name='UTC'):
    """Provide a timzeone-aware object for a given datetime and timezone name
    """
    import pytz
    assert dt.tzinfo == None
    utc = pytz.timezone('UTC')
    aware = utc.localize(dt)
    timezone = pytz.timezone(tz_name)
    tz_aware_dt = aware.astimezone(timezone)
    return tz_aware_dt

def is_url(url):
    """Check wheather given text is url or not
    """
    from urlparse import urlparse
    return bool(urlparse(url ).scheme)

def build_url(url, query):
    import urllib
    if not url.endswith('?'):
        url = url + '?'
    return url + urllib.urlencode(query)

def time_ago_in_words(from_time):
    try:
        from datetime import datetime
        from webhelpers2 import date
        logger.debug("from_time: %s, type=%s", from_time, type(from_time))
        delta = datetime.now() - from_time
        granularity='minute'
        if delta.days > 365:
            granularity = 'year'
        elif delta.days > 30:
            granularity = 'month'
        elif delta.days > 0:
            granularity = 'day'
        elif delta.total_seconds() > 3600:
            granularity = 'hour'
        time_ago = date.time_ago_in_words(from_time, granularity=granularity)
        time_ago = time_ago + " ago"
    except:
        time_ago = '???'
    finally:
        return time_ago

def root_path(path):
    try:
        return path.split(os.sep, 2)[1]
    except:
        return None
    
def appstruct_to_inputs(appstruct):
    import types
    inputs = []
    for key,values in appstruct.items():
        if type(values) != types.ListType:
            values = [values]
        for value in values:
            inputs.append( (str(key).strip(), str(value).strip()) )
    return inputs

