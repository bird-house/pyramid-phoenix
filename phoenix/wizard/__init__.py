from pyramid.settings import asbool
from pyramid.events import NewRequest

from twitcher.registry import service_registry_factory

from owslib.wps import WebProcessingService

import logging
logger = logging.getLogger(__name__)


def includeme(config):
    settings = config.registry.settings

    if asbool(settings.get('phoenix.wizard', True)):
        config.include('phoenix.wizard.views.start')
        config.include('phoenix.wizard.views.wps')
        config.include('phoenix.wizard.views.wpsprocess')
        config.include('phoenix.wizard.views.literalinputs')
        config.include('phoenix.wizard.views.complexinputs')
        config.include('phoenix.wizard.views.source')
        config.include('phoenix.wizard.views.esgfsearch')
        config.include('phoenix.wizard.views.threddsservice')
        config.include('phoenix.wizard.views.solrsearch')
        config.include('phoenix.wizard.views.done')

        # add malleefowl wps
        def add_wps(event):
            request = event.request
            # settings = event.request.registry.settings
            if not 'wps' in settings:
                logger.debug('register malleefowl wps service')
                try:
                    service_name = 'malleefowl'
                    registry = service_registry_factory(request.registry)
                    logger.debug("register: name=%s, url=%s", service_name, settings['wps.url'])
                    registry.register_service(name=service_name, url=settings['wps.url'], overwrite=True)
                    settings['wps'] = WebProcessingService(
                        url=request.route_url('owsproxy', service_name=service_name),
                        skip_caps=True, verify=False)
                except:
                    logger.exception('Could not connect malleefowl wps %s', settings['wps.url'])
            event.request.wps = settings.get('wps')
        config.add_subscriber(add_wps, NewRequest)

    # check if wizard is activated
    def wizard_activated(request):
        return asbool(settings.get('phoenix.wizard', 'false'))
    config.add_request_method(wizard_activated, reify=True)
