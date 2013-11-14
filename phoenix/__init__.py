# __init__.py
# Copyright (C) 2013 the ClimDaPs/Phoenix authors and contributors
# <see AUTHORS file>
#
# This module is part of ClimDaPs/Phoenix and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from pyramid.config import Configurator
from pyramid.events import subscriber
from pyramid.events import NewRequest
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from .security import groupfinder
from .resources import Root

import pymongo


from .helpers import button
import logging

log = logging.getLogger(__name__)

from deform import Form

def add_search_path():
    # register templates
    loader = Form.default_renderer.loader
   
    from os.path import dirname, join
    path = join(dirname(__file__), 'templates', 'deform')
    loader.search_path = (path,) + loader.search_path


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    log.debug("init phoenix application")
    log.debug("settings: %s", settings)

    # security
    authn_policy = AuthTktAuthenticationPolicy('s3cReT', callback=groupfinder, hashalg='sha512')
    authz_policy = ACLAuthorizationPolicy()
    config = Configurator(settings=settings, root_factory=Root)
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)

    # using mozilla persona
    config.include('pyramid_persona')

    # includes
    #config.include('deform_bootstrap')
    config.include('deform_bootstrap_extra')

    # add my own templates
    # TODO: improve config of my own templates
    # see also: http://docs.pylonsproject.org/projects/deform/en/latest/templates.html#overriding-for-all-forms
    # register template search path
    add_search_path()
    log.debug('search path= %s', Form.default_renderer.loader.search_path)

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
    config.add_route('catalog_wps_add', '/catalog/wps/add')
    config.add_route('catalog_wps_select', '/catalog/wps/select')
    config.add_route('tds', '/tds')
    config.add_route('processes', '/processes')
    config.add_route('jobs', '/jobs')
    config.add_route('output_details', '/output_details')
    config.add_route('execute', '/execute')
    config.add_route('monitor', '/monitor')
    config.add_route('admin', '/admin')
    config.add_route('wizard', '/wizard')
    config.add_route('help', '/help')
    config.add_route('login', '/login')
    config.add_route('login_persona', '/login/persona')
    config.add_route('login_openid', '/login/openid')

    # A quick access to the login button
    config.add_request_method(button, 'login_button', reify=True)

    # MongoDB
    # TODO: move this to models.py
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

