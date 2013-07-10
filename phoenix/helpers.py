import logging

log = logging.getLogger(__name__)

def get_service_url(request):
    settings = request.registry.settings
    # TODO: dont use hard coded project name
    service_url = settings.get('phoenix.wps', None)
    log.debug('using wps = %s', service_url)
    return service_url

def mongodb_conn(request):
	settings = request.registry.settings
	conn = settings.get('mongodb_conn', None)
	return conn