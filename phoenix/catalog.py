import logging
logger = logging.getLogger(__name__)

from .models import database
from .wps import get_wps

# catalog for wps
def add_wps(request, url, notes):
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
            notes = notes,
            )
        db.catalog.save(entry)
    except Exception as e:
        logger.warn('could not add wps %s, message=%s' % (url, e.message))
    
    return entry

def get_wps_list(request):
    db = database(request)
    return db.catalog.find(dict(format='WPS'))

def get_wps_list_as_tuple(request):
    return map(lambda entry: (entry['url'], entry['title']), get_wps_list(request))

