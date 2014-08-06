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
from .security import groupfinder, root_factory

import pymongo

from .helpers import button
import logging

logger = logging.getLogger(__name__)

from deform import Form

def add_search_path():
    # register templates
    loader = Form.default_renderer.loader
   
    from os.path import dirname, join
    path = join(dirname(__file__), 'templates', 'deform')
    loader.search_path = (path,) + loader.search_path


def main(global_config, **settings):
    """
    This function returns a Pyramid WSGI application.
    """

    # security
    authn_policy = AuthTktAuthenticationPolicy(
        'sosecret', callback=groupfinder, hashalg='sha512')
    authz_policy = ACLAuthorizationPolicy()
    config = Configurator(root_factory=root_factory, settings=settings)
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)

    # beaker session
    config.include('pyramid_beaker')

    # chameleon templates
    config.include('pyramid_chameleon')
    
    # deform
    config.include('deform_bootstrap')
    #config.include('deform_bootstrap_extra')

    # add my own templates
    # TODO: improve config of my own templates
    # see also: http://docs.pylonsproject.org/projects/deform/en/latest/templates.html#overriding-for-all-forms
    # register template search path
    add_search_path()
    #logger.debug('search path= %s', Form.default_renderer.loader.search_path)

    # static views (stylesheets etc)
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_static_view('deform_static', 'deform:static', cache_max_age=3600)
    config.add_static_view(
        'deform_bootstrap_static', 'deform_bootstrap:static',
        cache_max_age=3600
    )
    #config.add_static_view(
    #    'deform_bootstrap_extra_static', 'deform_bootstrap_extra:static',
    #    cache_max_age=3600
    #)

    # routes 
    config.add_route('home', '/')
    config.add_route('processes', '/processes')
    config.add_route('jobs', '/jobs')
    config.add_route('output_details', '/output_details')
    config.add_route('execute', '/execute')
  
    config.add_route('wizard', '/wizard')
    config.add_route('qc_wizard_check', '/qc_wizard_check')
    config.add_route('qc_wizard_yaml', '/qc_wizard_yaml')
    config.add_route('map', '/map')
    config.add_route('account', '/account')
    
    config.add_route('settings', '/settings')
    config.add_route('catalog', '/settings/catalog')
    config.add_route('user', '/settings/user')
    
    config.add_route('signin', '/signin')
    config.add_route('logout', '/logout')
    config.add_route('login_openid', '/login/openid')
    # TODO: need some work work on local accounts
    config.add_route('login_local', '/login/local')
    config.add_route('register', '/register')

    # wizard
    config.add_route('wizard_wps', '/wizard/wps')
    config.add_route('wizard_process', '/wizard/process')
    config.add_route('wizard_parameters', '/wizard/parameters')
    config.add_route('wizard_inputs', '/wizard/inputs')
    config.add_route('wizard_source', '/wizard/source')
    config.add_route('wizard_csw', '/wizard/csw')
    config.add_route('wizard_esgf', '/wizard/esgf')
    config.add_route('wizard_esgf_files', '/wizard/esgf_files')
    config.add_route('wizard_done', '/wizard/done')

    # A quick access to the login button
    config.add_request_method(button, 'login_button', reify=True)

    # MongoDB
    # TODO: maybe move this to models.py?
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

    # malleefowl wps
    def add_wps(event):
        settings = event.request.registry.settings
        event.request.wps = settings['wps']

    try:
        from owslib.wps import WebProcessingService
        config.registry.settings['wps'] = WebProcessingService(url=settings['wps.url'])
        config.add_subscriber(add_wps, NewRequest)
    except:
        logger.exception('Could not connect malleefowl wps %s', settings['wps.url'])

    # catalog service
    def add_csw(event):
        settings = event.request.registry.settings
        event.request.csw = settings['csw']

    try:
        from owslib.csw import CatalogueServiceWeb
        config.registry.settings['csw'] = CatalogueServiceWeb(url=settings['csw.url'])
        config.add_subscriber(add_csw, NewRequest)
    except:
        logger.exception('Could not connect catalog service %s', settings['csw.url'])
    
    config.scan('phoenix')

    return config.make_wsgi_app()

