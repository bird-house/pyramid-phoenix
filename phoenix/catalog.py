import logging
logger = logging.getLogger(__name__)

from .models import database
from .wps import get_wps

# catalog for wps
def add_wps_entry(request, url, username=None, password=None, notes=None):
    entry = None
    try:
        wps = get_wps(url)

        db = database(request)
        entry = db.catalog.find_one(dict(url = wps.url))
        if entry is not None:
            db.catalog.remove(dict(url = wps.url))
        entry = dict(
            format = 'WPS',
            url = wps.url,
            title = wps.identification.title,
            abstract = wps.identification.abstract,
            username = username,
            password = password,
            notes = notes,
            )
        db.catalog.save(entry)
    except Exception as e:
        logger.warn('could not add wps %s, message=%s' % (url, e.message))
    
    return entry

def delete_wps_entry(request, url):
    try:
        db = database(request)
        db.catalog.remove(dict(url=url))
    except Exception as e:
        logger.warn('could not delete wps %s in catalog, message=%s' % (url, e.message))

def get_wps_entry(request, url):
    entry = None
    try:
        db = database(request)
        entry = db.catalog.find_one(dict(url = url))
    except Exception as e:
        logger.warn('could not find wps %s in catalog, message=%s' % (url, e.message))
    return entry

def get_wps_list(request):
    db = database(request)
    return db.catalog.find(dict(format='WPS'))

def get_wps_list_as_tuple(request):
    return map(lambda entry: (entry['url'], '%s (%s)' % (entry.get('title', 'unknown'), entry.get('notes', ''))), get_wps_list(request))

