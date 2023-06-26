import os
from datetime import datetime
from urllib.parse import urlparse, urlencode

from owslib.util import build_get_url

import logging
LOGGER = logging.getLogger("PHOENIX")

# buttons
# see kotti: https://github.com/Kotti/Kotti
# TODO: maybe use deform.Button instead of ActionButton


class ActionButton(object):
    def __init__(self, name, title=None, no_children=False, href=None, new_window=False,
                 disabled=False, css_class="btn btn-outline-secondary",
                 icon=None):
        self.name = name
        if title is None:
            title = name.replace('-', ' ').replace('_', ' ').title()
        self.title = title
        self.no_children = no_children
        self.css_class = css_class
        if disabled:
            self.css_class = self.css_class + " disabled"
        self.icon = icon
        if href is None:
            href = '/' + self.name
        self.href = href
        self.new_window = new_window

    def url(self, context, request):
        return self.href

    def permitted(self, context, request):
        return True

    def __eq__(self, other):
        return isinstance(other, ActionButton) and repr(self) == repr(other)

    def __repr__(self):
        return 'ActionButton({0}, {1})'.format(self.name, self.title)

# processes


def pinned_processes(request):
    from owslib.wps import WebProcessingService
    settings = request.db.settings.find_one() or {}
    processes = []
    if 'pinned_processes' in settings:
        for pinned in settings.get('pinned_processes'):
            try:
                service_name, identifier = pinned.split('.', 1)
                url = request.route_path(
                    'processes_execute', _query=[('wps', service_name), ('process', identifier)])
                wps = WebProcessingService(
                    url=request.route_url('owsproxy', service_name=service_name), verify=False)
                # TODO: need to fix owslib to handle special identifiers
                process = wps.describeprocess(identifier)
                description = headline(process.abstract)
            except Exception:
                LOGGER.warn("could not add pinned process %s", pinned)
            else:
                processes.append(dict(
                    title=process.identifier,
                    description=description,
                    url=url,
                    service_title=wps.identification.title))
    return processes


# csrf

def skip_csrf_token(appstruct):
    if 'csrf_token' in appstruct:
        del appstruct['csrf_token']
    return appstruct


# misc

def headline(text, max_length=120):
    if text:
        if max_length < 25:
            max_length = 25
        elif max_length > 120:
            max_length = 120
        caption = text.split('.', 1)[0].strip() + '.'
        if len(caption) > max_length:
            caption = "{} ...".format(caption[:max_length - 4])
    else:
        caption = "No summary"
    return caption


def make_tags(tags_str):
    tags = [tag.strip().lower() for tag in tags_str.split(',') if len(tag.strip()) > 0]
    # remove duplicates
    tags = set(tags)
    # and special tags
    if 'private' in tags:
        tags.remove('private')
    if 'all' in tags:
        tags.remove('all')
    tags = list(tags)
    # ... and sort list
    tags.sort()
    return tags


def format_tags(tags):
    if tags is None:
        tags = []
    return ', '.join(tags)


def localize_datetime(dt, tz_name='UTC'):
    """Provide a timzeone-aware object for a given datetime and timezone name
    """
    import pytz
    assert dt.tzinfo is None
    utc = pytz.timezone('UTC')
    aware = utc.localize(dt)
    timezone = pytz.timezone(tz_name)
    tz_aware_dt = aware.astimezone(timezone)
    return tz_aware_dt


def is_url(url):
    """Check wheather given text is url or not
    """
    return bool(urlparse(url).scheme)


def build_url(url, query):
    if not url.endswith('?'):
        url = url + '?'
    return url + urlencode(query)


def wps_caps_url(url):
    # TODO: move code to owslib?
    # TODO: patch for cows wps
    from collections import OrderedDict
    params = OrderedDict()
    params['Service'] = 'WPS'
    params['Request'] = 'GetCapabilities'
    params['Version'] = '1.0.0'
    # Service=WPS&Request=GetCapabilities&Version=1.0.0
    # params = {'service': 'WPS', 'request': 'GetCapabilities', 'version': '1.0.0'}
    return build_get_url(url, params, overwrite=True)


def wps_describe_url(url, identifier):
    # TODO: move code to owslib?
    # TODO: patch for cows wps
    from collections import OrderedDict
    params = OrderedDict()
    params['Service'] = 'WPS'
    params['Request'] = 'DescribeProcess'
    params['Version'] = '1.0.0'
    params['Identifier'] = identifier
    # params = {'service': 'WPS', 'request': 'DescribeProcess', 'version': '1.0.0', 'identifier': identifier}
    return build_get_url(url, params, overwrite=True)


def time_ago_in_words(from_time):
    from webhelpers2.date import time_ago_in_words as _time_ago_in_words
    try:
        delta = datetime.now() - from_time
        granularity = 'minute'
        if delta.days > 365:
            granularity = 'year'
        elif delta.days > 30:
            granularity = 'month'
        elif delta.days > 0:
            granularity = 'day'
        elif delta.total_seconds() > 3600:
            granularity = 'hour'
        time_ago = _time_ago_in_words(from_time, granularity=granularity)
        time_ago = time_ago + " ago"
    except Exception:
        time_ago = '???'
    finally:
        return time_ago


def root_path(path):
    try:
        return path.split(os.sep, 2)[1]
    except Exception:
        return None
