from pyramid.settings import asbool
from pyramid.events import NewRequest

from twitcher.registry import service_registry_factory
from twitcher.registry import proxy_url

from owslib.wps import WebProcessingService

import logging
logger = logging.getLogger(__name__)


def includeme(config):
    settings = config.registry.settings

    if asbool(settings.get('phoenix.wizard', True)):
        # logger.debug('Add wizard')

        # views
        config.add_route('wizard', '/wizard')
        config.add_route('wizard_wps', '/wizard/wps')
        config.add_route('wizard_process', '/wizard/process')
        config.add_route('wizard_literal_inputs', '/wizard/literal_inputs')
        config.add_route('wizard_complex_inputs', '/wizard/complex_inputs')
        config.add_route('wizard_source', '/wizard/source')
        # config.add_route('wizard_solr', '/wizard/solr')
        config.add_route('wizard_csw', '/wizard/csw')
        config.add_route('wizard_csw_select', '/wizard/csw/{recordid}/select.json')
        config.add_route('wizard_esgf_search', '/wizard/esgf_search')
        config.add_route('wizard_esgf_login', '/wizard/esgf_login')
        config.add_route('wizard_loading', '/wizard/loading')
        config.add_route('wizard_check_logon', '/wizard/check_logon.json')
        config.add_route('wizard_swift_login', '/wizard/swift_login')
        config.add_route('wizard_swiftbrowser', '/wizard/swiftbrowser')
        config.add_route('wizard_threddsservice', '/wizard/threddsservice')
        config.add_route('wizard_threddsbrowser', '/wizard/threddsbrowser')
        config.add_route('wizard_upload', '/wizard/upload')
        config.add_route('wizard_storage', '/wizard/storage')
        config.add_route('wizard_done', '/wizard/done')

        config.include('phoenix.wizard.views.solrsearch')

        # add malleefowl wps
        def add_wps(event):
            request = event.request
            # settings = event.request.registry.settings
            if settings.get('wps') is None:
                try:
                    service_name = 'malleefowl'
                    registry = service_registry_factory(request.registry)
                    logger.debug("register: name=%s, url=%s", service_name, settings['wps.url'])
                    try:
                        registry.get_service_by_url(settings['wps.url'])
                    except ValueError:
                        # TODO: we need to register wps when proxy service is up
                        registry.register_service(name=service_name, url=settings['wps.url'])
                    else:
                        settings['wps'] = WebProcessingService(url=proxy_url(request, service_name), skip_caps=True,
                                                               verify=False)
                except:
                    logger.exception('Could not connect malleefowl wps %s', settings['wps.url'])
            else:
                logger.debug("wps already initialized")
            event.request.wps = settings.get('wps')
        config.add_subscriber(add_wps, NewRequest)
        
    # check if wizard is activated
    def wizard_activated(request):
        # settings = request.registry.settings
        return asbool(settings.get('phoenix.wizard', True))
    config.add_request_method(wizard_activated, reify=True)
