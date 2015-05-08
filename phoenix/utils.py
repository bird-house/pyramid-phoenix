import logging
logger = logging.getLogger(__name__)

SIGNIN_HTML = '<a class="navbar-link" href="%s"><i class="glyphicon glyphicon-log-in"></i> Sign in</a>'
SIGNOUT_HTML = '<a class="navbar-link" href="%s" id="signout" title="Logout %s"><i class="glyphicon glyphicon-log-out"></i> Sign out</a>'

def button(request):
    """If the user is logged in, returns the logout button, otherwise returns the login button"""
    import markupsafe
    from pyramid.security import authenticated_userid
    if not authenticated_userid(request):
        return markupsafe.Markup(SIGNIN_HTML) % (request.route_path('account_login', protocol='esgf'))
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
        from webhelpers2 import date
        #logger.debug("from_time: %s, type=%s", from_time, type(from_time))
        time_ago = date.time_ago_in_words(from_time, granularity='minute')
        time_ago = time_ago + " ago"
    except:
        time_ago = '???'
    finally:
        return time_ago
    
    




    


