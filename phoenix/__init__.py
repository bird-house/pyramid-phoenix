__version__ = '0.11.0'


def main(global_config, **settings):
    """
    This function returns a Pyramid WSGI application.
    """
    from pyramid.config import Configurator

    config = Configurator(settings=settings, autocommit=False)

    # security
    config.include('phoenix.security')

    # beaker session
    config.include('pyramid_beaker')

    # chameleon templates
    config.include('pyramid_chameleon')

    # deform
    # config.include('pyramid_deform')
    # config.include('js.deform')

    # celery
    config.include('pyramid_celery')
    config.configure_celery(global_config['__file__'])

    # static views (stylesheets etc)
    config.add_static_view('static', 'static')
    config.add_static_view('static_deform', 'deform:static')

    # database
    # TODO: overwrite request.db from twitcher
    # See: http://docs.pylonsproject.org/projects/pyramid/en/latest/api/config.html
    # config.include('phoenix.db')
    from phoenix.db import includeme as include_db
    include_db(config)

    # routes
    config.add_route('home', '/')

    # storage
    config.include('phoenix.storage')

    # settings
    config.include('phoenix.settings')

    # account
    config.include('phoenix.account')

    # dashboard
    config.include('phoenix.dashboard')

    # processes
    config.include('phoenix.processes')

    # job monitor
    config.include('phoenix.monitor')

    # user profiles
    config.include('phoenix.people')

    # catalog
    config.include('phoenix.catalog')

    # service settings
    config.include('phoenix.services')

    # readthedocs
    config.add_route('readthedocs', 'https://pyramid-phoenix.readthedocs.org/')

    # max file size for upload in MB
    def max_file_size(request):
        settings = request.registry.settings
        return int(settings.get('phoenix.max_file_size', '200'))
    config.add_request_method(max_file_size, reify=True)

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
    # def wpsexception_adapter(obj, request):
    #     logger.debug("mongo adapter wpsexception called")
    #     return '%s %s: %s' % (obj.code, obj.locator, obj.text)
    # from owslib import wps
    # json_renderer.add_adapter(wps.WPSException, wpsexception_adapter)
    config.add_renderer('json', json_renderer)

    config.scan('phoenix')

    # enable autocommit
    config.autocommit = True

    return config.make_wsgi_app()
