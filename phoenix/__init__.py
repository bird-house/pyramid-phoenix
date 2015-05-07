from pyramid.config import Configurator
from pyramid.events import subscriber
from pyramid.events import NewRequest
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from phoenix.security import groupfinder, root_factory

import pymongo

from phoenix.utils import button
import logging

logger = logging.getLogger(__name__)

from deform import Form

## def add_search_path():
##     # register templates
##     loader = Form.default_renderer.loader
   
##     from os.path import dirname, join
##     path = join(dirname(__file__), 'templates', 'deform')
##     loader.search_path = (path,) + loader.search_path


def main(global_config, **settings):
    """
    This function returns a Pyramid WSGI application.
    """

    # security
    authn_policy = AuthTktAuthenticationPolicy(
        'tellnoone', callback=groupfinder, hashalg='sha512')
    authz_policy = ACLAuthorizationPolicy()
    config = Configurator(root_factory=root_factory, settings=settings)
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)

    # beaker session
    config.include('pyramid_beaker')

    # chameleon templates
    config.include('pyramid_chameleon')
    
    # deform
    #config.include('pyramid_deform')
    #config.include('js.deform')

    # mailer
    config.include('pyramid_mailer')

    # add my own templates
    # TODO: improve config of my own templates
    # see also: http://docs.pylonsproject.org/projects/deform/en/latest/templates.html#overriding-for-all-forms
    # register template search path
    #add_search_path()
    #logger.debug('search path= %s', Form.default_renderer.loader.search_path)

    # static views (stylesheets etc)
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_static_view('deform_static', 'deform:static', cache_max_age=3600)

    # routes 
    config.add_route('home', '/')

    # login
    config.add_route('signin', '/signin/{tab}')
    config.add_route('logout', '/logout')
    config.add_route('login_openid', '/login/openid')
    config.add_route('register', '/register')

    # dashboard
    config.add_route('dashboard', '/dashboard/{tab}')
    
    # processes
    config.add_route('processes_overview', '/processes/overview')
    config.add_route('processes_list', '/processes/list')
    config.add_route('processes_execute', '/processes/execute')

    # myjobs
    config.add_route('myjobs_overview', '/myjobs/overview')
    config.add_route('myjobs_details', '/myjobs/details/{jobid}/{tab}')
    config.add_route('update_myjobs', '/myjobs/update.json')
    config.add_route('remove_myjobs', '/myjobs/remove_all')
    config.add_route('remove_myjob', '/myjobs/{jobid}/remove')
    
    # my account
    config.add_route('myaccount', '/myaccount/{tab}')

    # settings
    config.add_route('settings', '/settings/overview')
    config.add_route('settings_catalog', '/settings/catalog')
    config.add_route('settings_add_service', '/settings/catalog/add_service')
    config.add_route('settings_add_dataset', '/settings/catalog/add_dataset')
    config.add_route('remove_record', '/settings/catalog/{recordid}/remove')
    config.add_route('remove_all_records', '/settings/catalog/remove_all')
    config.add_route('settings_users', '/settings/users')
    config.add_route('settings_edit_user', '/settings/users/{email}/edit')
    config.add_route('remove_user', '/settings/users/{email}/remove')
    config.add_route('settings_jobs', '/settings/jobs')
    config.add_route('remove_all_jobs', '/settings/jobs/remove_all')

    # wizard
    config.add_route('wizard', '/wizard/start')
    config.add_route('wizard_wps', '/wizard/wps')
    config.add_route('wizard_process', '/wizard/process')
    config.add_route('wizard_literal_inputs', '/wizard/literal_inputs')
    config.add_route('wizard_complex_inputs', '/wizard/complex_inputs')
    config.add_route('wizard_source', '/wizard/source')
    config.add_route('wizard_csw', '/wizard/csw')
    config.add_route('wizard_csw_select', '/wizard/csw/{recordid}/select.json')
    config.add_route('wizard_esgf_search', '/wizard/esgf_search')
    config.add_route('wizard_esgf_login', '/wizard/esgf_login')
    config.add_route('wizard_swift_login', '/wizard/swift_login')
    config.add_route('wizard_swiftbrowser', '/wizard/swiftbrowser')
    config.add_route('wizard_done', '/wizard/done')

    # A quick access to the login button
    config.add_request_method(button, 'login_button', reify=True)

    # use json_adapter for datetime
    # http://docs.pylonsproject.org/projects/pyramid/en/1.5-branch/narr/renderers.html#json-renderer
    from pyramid.renderers import JSON
    import datetime
    json_renderer = JSON()
    def datetime_adapter(obj, request):
        return obj.isoformat()
    json_renderer.add_adapter(datetime.datetime, datetime_adapter)
    import bson
    def objectid_adapter(obj, request):
        return str(obj)
    json_renderer.add_adapter(bson.objectid.ObjectId, objectid_adapter)
    ## def wpsexception_adapter(obj, request):
    ##     logger.debug("mongo adapter wpsexception called")
    ##     return '%s %s: %s' % (obj.code, obj.locator, obj.text)
    ## from owslib import wps
    ## json_renderer.add_adapter(wps.WPSException, wpsexception_adapter)
    config.add_renderer('json', json_renderer)

    # MongoDB
    # TODO: maybe move this to models.py?
    #@subscriber(NewRequest)
    def add_mongodb(event):
        settings = event.request.registry.settings
        if settings.get('db') is None:
            try:
                MongoDB = pymongo.Connection
                if 'pyramid_debugtoolbar' in set(settings.values()):
                    class MongoDB(pymongo.Connection):
                        def __html__(self):
                            return 'MongoDB: <b>{}></b>'.format(self)
                conn = MongoDB(settings['mongodb.url'])
                settings['db'] = conn[settings['mongodb.db_name']]
                logger.debug("Connected to mongodb %s.", settings['mongodb.url'])
            except:
                logger.exception('Could not connect to mongodb %s.', settings['mongodb.url'])
        event.request.db = settings.get('db')
    config.add_subscriber(add_mongodb, NewRequest)
    
    # malleefowl wps
    # TODO: subscriber annotation does not work
    #@subscriber(NewRequest)
    def add_wps(event):
        settings = event.request.registry.settings
        if settings.get('wps') is None:
            try:
                from owslib.wps import WebProcessingService
                settings['wps'] = WebProcessingService(url=settings['wps.url'])
                logger.debug('Connected to malleefowl wps %s', settings['wps.url'])
            except:
                logger.exception('Could not connect malleefowl wps %s', settings['wps.url'])
        event.request.wps = settings.get('wps')
    config.add_subscriber(add_wps, NewRequest)
        
    # catalog service
    #@subscriber(NewRequest)
    def add_csw(event):
        settings = event.request.registry.settings
        if settings.get('csw') is None:
            try:
                from owslib.csw import CatalogueServiceWeb
                settings['csw'] = CatalogueServiceWeb(url=settings['csw.url'])
                logger.debug('Connected to catalog service %s', settings['csw.url'])
            except:
                logger.exception('Could not connect catalog service %s', settings['csw.url'])
        event.request.csw = settings.get('csw')
    config.add_subscriber(add_csw, NewRequest)
    
    config.scan('phoenix')

    return config.make_wsgi_app()

