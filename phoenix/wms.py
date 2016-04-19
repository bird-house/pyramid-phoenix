from pyramid.settings import asbool

import logging
logger = logging.getLogger(__name__)

def includeme(config):
    settings = config.registry.settings

    if asbool(settings.get('phoenix.wms', True)):
        logger.info('Add WMS')

    # check if wms is activated
    def wms_activated(request):
        settings = request.registry.settings
        return asbool(settings.get('phoenix.wms', True))
    config.add_request_method(wms_activated, reify=True)
