# MongoDB
# http://docs.pylonsproject.org/projects/pyramid-cookbook/en/latest/database/mongodb.html
# maybe use event to register mongodb

import pymongo


def mongodb(registry):
    settings = registry.settings
    db = registry.db[settings['mongodb.db_name']]
    return db


def includeme(config):
    settings = config.get_settings()
    config.registry.db = pymongo.MongoClient(
        settings['mongodb.host'],
        int(settings['mongodb.port']))

    def add_db(event):
        return mongodb(event.registry)
    config.add_request_method(add_db, 'db', reify=True)
