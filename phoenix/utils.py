import os
import tempfile
import deform

from pyramid.security import authenticated_userid
from phoenix.security import auth_protocols

import logging
logger = logging.getLogger(__name__)

SIGNIN_HTML = '<a class="navbar-link btn-lg" href="%s" data-toggle="tooltip" title="Sign in"><span class="fa fa-sign-in"></span></a>'
SIGNOUT_HTML = '<a class="navbar-link btn-lg" href="%s" data-toggle="tooltip" title="Sign out %s"><span class="fa fa-sign-out"></span></a>'

# upload helpers

def save_upload(request, filename, fs=None):
    folder=authenticated_userid(request)
    path = os.path.join(folder, os.path.basename(filename))
    if request.storage.exists(path):
        request.storage.delete(path)
    stored_filename = None
    if fs is None:
        stored_filename = request.storage.save_filename(filename, folder=folder)
    else:
        stored_filename = request.storage.save_file(fs.file, filename=os.path.basename(path), folder=folder)
    logger.debug('saved file to upload storage %s', stored_filename)

    
def save_chunk(fs, path):
    """
    Save an uploaded chunk.
    
    Chunks are stored in chunks/
    """
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    with open(path, 'wb+') as destination:
        destination.write(fs.read())

        
def combine_chunks(total_parts, source_folder, dest):
    """
    Combine a chunked file into a whole file again. Goes through each part
    , in order, and appends that part's bytes to another destination file.
    
    Chunks are stored in chunks/
    """

    logger.debug("Combining chunks: %s", source_folder)
    
    if not os.path.exists(os.path.dirname(dest)):
        os.makedirs(os.path.dirname(dest))

    with open(dest, 'wb+') as destination:
        for i in xrange(int(total_parts)):
            part = os.path.join(source_folder, str(i))
            with open(part, 'rb') as source:
                destination.write(source.read())
        logger.debug("Combined: %s", dest)

# misc


def button(request):
    """If the user is logged in, returns the logout button, otherwise returns the login button"""
    import markupsafe
    
    if not authenticated_userid(request):
        protocols = auth_protocols(request)
        if len(protocols) > 0:
            protocol = protocols[-1]
        else:
            protocol = 'oauth2'
        return markupsafe.Markup(SIGNIN_HTML) % (request.route_path('account_login', protocol=protocol))
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
    
