from pyramid.settings import asbool
from pyramid.events import NewRequest

from phoenix.catalog.catalog import *

def includeme(config):
    settings = config.registry.settings

    # catalog service
    if asbool(settings.get('phoenix.csw', True)):
        logger.info('Add catalog')
        
        def add_csw(event):
            settings = event.request.registry.settings
            if settings.get('csw') is None:
                try:
                    from owslib.csw import CatalogueServiceWeb
                    settings['csw'] = CatalogueServiceWeb(url=settings['csw.url'])
                    logger.debug("init csw")
                except:
                    logger.exception('Could not connect catalog service %s', settings['csw.url'])
            else:
                logger.debug("csw already initialized")
            event.request.csw = settings.get('csw')
        config.add_subscriber(add_csw, NewRequest)

    # check if csw is activated
    def csw_activated(request):
        settings = request.registry.settings
        return asbool(settings.get('phoenix.csw', True))
    config.add_request_method(csw_activated, reify=True)
