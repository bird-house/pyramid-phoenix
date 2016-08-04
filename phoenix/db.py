# MongoDB
# http://docs.pylonsproject.org/projects/pyramid-cookbook/en/latest/database/mongodb.html
# maybe use event to register mongodb   

import pymongo

from pyramid.events import NewRequest

import logging
logger = logging.getLogger(__name__)


def mongodb(registry):
    settings = registry.settings
    client = pymongo.MongoClient(settings['mongodb.host'], int(settings['mongodb.port']))
    db = client[settings['mongodb.db_name']]
    #db.services.create_index("name", unique=True)
    return db


def includeme(config):
    def _add_db(event):
        settings = event.request.registry.settings
        if settings.get('db') is None:
            try:
                settings['db'] = mongodb(event.request.registry)
                logger.debug("init db")
            except:
                logger.exception('Could not connect mongodb.')
            else:
                logger.debug("db already initialized")
        event.request.db = settings.get('db')
    config.add_subscriber(_add_db, NewRequest)
