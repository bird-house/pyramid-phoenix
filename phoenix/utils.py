import logging
logger = logging.getLogger(__name__)

SIGNIN_HTML = '<a href="/signin/esgf"><i class="glyphicon glyphicon-user"></i> Sign in</a>'
SIGNOUT_HTML = '<a href="/logout" id="signout" title="Logout %s"><i class="glyphicon glyphicon-off"></i> Sign out</a>'

def button(request):
    """If the user is logged in, returns the logout button, otherwise returns the login button"""
    import markupsafe
    from pyramid.security import authenticated_userid
    if not authenticated_userid(request):
        return markupsafe.Markup(SIGNIN_HTML)
    else:
        return markupsafe.Markup(SIGNOUT_HTML) % (authenticated_userid(request))


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




    


