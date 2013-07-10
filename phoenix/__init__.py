from pyramid.config import Configurator
from pyramid.events import subscriber
from pyramid.events import NewRequest
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy

import pymongo

from sqlalchemy import engine_from_config
from sqlalchemy.exc import IntegrityError
import transaction

from .resources import Root
from .models import DBSession, Base, Status
import logging

log = logging.getLogger(__name__)

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    log.debug("init phoenix application")

    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine

    ## Initial Database Setup #################################################
    session = DBSession()

    try:
        Base.metadata.create_all(engine)

        # Order is important!
        session.add(Status('Running'))
        session.add(Status('Completed'))
        session.add(Status('Cancelled'))
        session.add(Status('Failed'))

        session.flush()
        transaction.commit()
    except IntegrityError:
        transaction.abort()
        session = DBSession()
    
    ###########################################################################

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

    deform_templates = resource_filename('deform', 'templates')
    deform_bootstrap_templates = resource_filename('deform_bootstrap', 'templates')
    own_templates = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                 'templates/deform'))
    search_path = (own_templates, deform_bootstrap_templates, deform_templates)

    Form.set_zpt_renderer(search_path)

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
    #config.add_route('signup', '/signup')
    #config.add_route('login', '/login')
    #config.add_route('profile', '/profile')
    #config.add_route('logout', '/logout')
    config.add_route('form', '/form')
    config.add_route('monitor', '/monitor')
    config.add_route('help', '/help')

    #config.scan('.layouts')
    #config.scan('.panels')
    #config.scan('.views')

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

