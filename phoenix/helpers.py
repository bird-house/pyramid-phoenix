import logging

log = logging.getLogger(__name__)

def wps_url(request):
    settings = request.registry.settings
    # TODO: dont use hard coded project name
    service_url = settings.get('phoenix.wps', None)
    log.debug('using wps = %s', service_url)
    return service_url

def update_wps_url(request, wps_url):
    settings = request.registry.settings
    settings['phoenix.wps'] = wps_url
   
def csw_url(request):
    settings = request.registry.settings
    # TODO: dont use hard coded project name
    service_url = settings.get('phoenix.csw', None)
    log.debug('using csw = %s', service_url)
    return service_url

def whitelist(request):
	settings = request.registry.settings
	whitelist_str = settings.get('phoenix.login.whitelist', '')
	whitelist = whitelist_str.split(',')
	return whitelist

def mongodb_conn(request):
	settings = request.registry.settings
	conn = settings.get('mongodb_conn', None)
	return conn

def is_url(text):
    """Check wheather given text is url or not

    TODO: code is taken from pywps. Maybe there is a better alternative.
    """
        
    try:
        (urltype, opaquestring) = urllib.splittype(text)

        if urltype in ["http","https","ftp"]:
            return True
        else:
            return False
    except:
        return False