import logging
logger = logging.getLogger(__name__)

__version__ = (0, 4, 5, 'final', 1)

def get_version():
    import phoenix.version
    return phoenix.version.get_version(__version__)

def main(global_config, **settings):
    """
    This function returns a Pyramid WSGI application.
    """
    from pyramid.config import Configurator
    from pyramid.events import subscriber
    from pyramid.events import NewRequest
    from pyramid.authentication import AuthTktAuthenticationPolicy
    from pyramid.authorization import ACLAuthorizationPolicy
    from phoenix.security import groupfinder, root_factory

    # security
    # TODO: move to security
    authn_policy = AuthTktAuthenticationPolicy(
        settings.get('authomatic.secret'), callback=groupfinder, hashalg='sha512')
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

    # celery
    config.include('pyramid_celery')
    config.configure_celery(global_config['__file__'])

    # ldap
    config.include('pyramid_ldap')
    # FK: Ldap setup functions will be called on demand.

    # static views (stylesheets etc)
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_static_view('deform_static', 'deform:static', cache_max_age=3600)

    # routes 
    config.add_route('home', '/')

    # login
    config.add_route('account_login', '/account/login/{protocol}')
    config.add_route('account_logout', '/account/logout')
    config.add_route('account_auth', '/account/auth/{provider_name}')
    config.add_route('account_register', '/account/register')

    # dashboard
    config.add_route('dashboard', '/dashboard/{tab}')
    
    # processes
    config.add_route('processes', '/processes')
    config.add_route('processes_list', '/processes/list')
    config.add_route('processes_execute', '/processes/execute')

    # job monitor
    config.add_route('monitor', '/monitor')
    config.add_route('remove_job', '/monitor/{job_id}/remove')
    config.add_route('remove_all_jobs', '/monitor/remove_all')
    config.add_route('update_myjobs', '/monitor/update.json')
    config.add_route('monitor_details', '/monitor/{job_id}/{tab}')

    # user profile
    config.add_route('profile', '/profile/{tab}')

    # settings
    config.add_route('settings', '/settings')
    config.add_route('settings_users', '/settings/users')
    config.add_route('settings_edit_user', '/settings/users/{userid}/edit')
    config.add_route('remove_user', '/settings/users/{userid}/remove')
    config.add_route('settings_monitor', '/settings/monitor')
    config.add_route('settings_auth', '/settings/auth')
    config.add_route('settings_ldap', '/settings/ldap')
    config.add_route('settings_solr', '/settings/solr/{tab}')

    # supervisor
    config.add_route('supervisor', '/supervisor')
    config.add_route('supervisor_process', '/supervisor/{action}/{name}')
    config.add_route('supervisor_log', '/supervisor_log/{name}')

    # services
    config.add_route('services', '/services')
    config.add_route('register_service', '/services/register')
    config.add_route('service_details', '/services/{service_id}')
    config.add_route('remove_service', '/services/{service_id}/remove')

    # solr
    config.add_route('index_service', '/solr/{service_id}/index')
    config.add_route('clear_index', '/solr/clear')
    
    # wizard
    config.add_route('wizard', '/wizard')
    config.add_route('wizard_wps', '/wizard/wps')
    config.add_route('wizard_process', '/wizard/process')
    config.add_route('wizard_literal_inputs', '/wizard/literal_inputs')
    config.add_route('wizard_complex_inputs', '/wizard/complex_inputs')
    config.add_route('wizard_source', '/wizard/source')
    config.add_route('wizard_solr', '/wizard/solr')
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
    config.add_route('wizard_done', '/wizard/done')

    # wizard actions
    config.add_route('wizard_clear_favorites', '/wizard/clear_favorites')

    # readthedocs
    config.add_route('readthedocs', 'https://pyramid-phoenix.readthedocs.org/en/latest/{part}.html')

    # A quick access to the login button
    from phoenix.utils import button
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
                from phoenix.models import mongodb
                settings['db'] = mongodb(event.request.registry)
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
            except:
                logger.exception('Could not connect catalog service %s', settings['csw.url'])
        event.request.csw = settings.get('csw')
    config.add_subscriber(add_csw, NewRequest)
    
    config.scan('phoenix')

    return config.make_wsgi_app()

