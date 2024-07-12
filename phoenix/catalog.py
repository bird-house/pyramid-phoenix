from mako.template import Template
import re
import uuid
from os.path import join, dirname
from collections import namedtuple

import requests
from owslib.wps import WebProcessingService


from pyramid.settings import asbool
from pyramid.events import NewRequest

from phoenix.db import mongodb

import logging
LOGGER = logging.getLogger("PHOENIX")


def includeme(config):

    # catalog service
    def add_catalog(event):
        settings = event.request.registry.settings
        if settings.get('catalog') is None:
            try:
                settings['catalog'] = catalog_factory(config.registry)
            except Exception:
                LOGGER.warning('Could not connect catalog service.')
        event.request.catalog = settings.get('catalog')
    config.add_subscriber(add_catalog, NewRequest)


def catalog_factory(registry):
    db = mongodb(registry)
    return MongodbCatalog(db.catalog)


def _fetch_wps_metadata(url, title=None):
    """Fetch capabilities metadata from wps service and return record dict."""
    wps = WebProcessingService(url, verify=False, skip_caps=False)
    record = dict(
        title=title or wps.identification.title or "Unknown",
        abstract=getattr(wps.identification, 'abstract', ''),
        url=wps.url,
        creator=wps.provider.name,
        keywords=getattr(wps.identification, 'keywords', []),
        rights=getattr(wps.identification, 'accessconstraints', ''),
    )
    return record


class Catalog(object):
    def get_record_by_id(self, identifier):
        raise NotImplementedError

    def delete_record(self, identifier):
        raise NotImplementedError

    def insert_record(self, record):
        raise NotImplementedError

    def harvest(self, url, service_title=None, public=False):
        raise NotImplementedError

    def get_services(self, maxrecords=100):
        raise NotImplementedError

    def clear_services(self):
        raise NotImplementedError


def doc2record(document):
    """Converts ``document`` from mongodb to a ``Record`` object."""
    record = None
    if isinstance(document, dict):
        if '_id' in document:
            # _id field not allowed in record
            del document["_id"]
        record = namedtuple('Record', list(document.keys()))(*list(document.values()))
    return record


class MongodbCatalog(Catalog):
    """Implementation of a Catalog with MongoDB."""

    def __init__(self, collection):
        self.collection = collection

    def get_record_by_id(self, identifier):
        """
        Gets database record by identifier or title.

        If the identifier does not match, then a case-insensitive
        match is made on the title (replacing "_" with " "). This
        enables _deterministic_ URLs in which the WPS can be identified
        by a meaningful string as well as the standard long identifier.
        """
        doc = self.collection.find_one({'identifier': identifier})

        if not doc:
            title_regex = re.compile('^' + re.escape(identifier.replace('_', ' ')) + '$', re.IGNORECASE)
            doc = self.collection.find_one({'title': title_regex}) 

        return doc2record(doc)

    def delete_record(self, identifier):
        self.collection.delete_one({'identifier': identifier})

    def insert_record(self, record):
        record['identifier'] = uuid.uuid4().hex
        self.collection.save(record)

    def harvest(self, url, service_title=None, public=False, group=None):
        try:
            # fetch metadata
            record = _fetch_wps_metadata(url, title=service_title)
            record['public'] = public
            record['group'] = group
            self.insert_record(record)
        except Exception:
            LOGGER.warning("could not harvest metadata")
            raise Exception("could not harvest metadata")

    def get_services(self, maxrecords=100):
        return [doc2record(doc) for doc in self.collection.find()]

    def clear_services(self):
        self.collection.drop()
