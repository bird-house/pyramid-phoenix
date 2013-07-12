from pyramid.config import Configurator
from pyramid.events import subscriber
from pyramid.events import NewRequest
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy

import pymongo

from .resources import Root
import logging

log = logging.getLogger(__name__)

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    log.debug("init phoenix application")

    config = Configurator(settings=settings, root_factory=Root)

    # using mozilla persona
    config.include('pyramid_persona')

    # includes
    config.include('deform_bootstrap')
    #config.include('deform_bootstrap_extra')

    # add my own templates
    # TODO: improve config of my own templates
    # see also: http://docs.pylonsproject.org/projects/deform/en/latest/templates.html#overriding-for-all-forms
    from pkg_resources import resource_filename
    from deform import Form
    import os

    # static views (stylesheets etc)
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_static_view('deform_static', 'deform:static', cache_max_age=3600)
    config.add_static_view(
        'deform_bootstrap_static', 'deform_bootstrap:static',
        cache_max_age=3600
    )
    config.add_static_view(
        'deform_bootstrap_extra_static', 'deform_bootstrap_extra:static',
        cache_max_age=3600
    )

    # routes 
    config.add_route('home', '/')
    config.add_route('processes', '/processes')
    config.add_route('history', '/history')
    config.add_route('output_details', '/output_details')
    config.add_route('form', '/form')
    config.add_route('monitor', '/monitor')
    config.add_route('help', '/help')

     # MongoDB
    def add_mongo_db(event):
        settings = event.request.registry.settings
        url = settings['mongodb.url']
        db_name = settings['mongodb.db_name']
        db = settings['mongodb_conn'][db_name]
        event.request.db = db
    db_uri = settings['mongodb.url']
    MongoDB = pymongo.Connection
    if 'pyramid_debugtoolbar' in set(settings.values()):
        class MongoDB(pymongo.Connection):
            def __html__(self):
                return 'MongoDB: <b>{}></b>'.format(self)
    conn = MongoDB(db_uri)
    config.registry.settings['mongodb_conn'] = conn
    config.add_subscriber(add_mongo_db, NewRequest)
    config.scan('phoenix')

    return config.make_wsgi_app()

