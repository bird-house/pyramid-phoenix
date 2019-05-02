from mako.template import Template
import uuid
from os.path import join, dirname
from collections import namedtuple

import requests
from owslib.wps import WebProcessingService


from pyramid.settings import asbool
from pyramid.events import NewRequest

from phoenix.db import mongodb
from phoenix.twitcherclient import twitcher_service_factory

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
                LOGGER.exception('Could not connect catalog service.')
        else:
            LOGGER.debug("catalog already initialized")
        event.request.catalog = settings.get('catalog')
    config.add_subscriber(add_catalog, NewRequest)


def catalog_factory(registry):
    service_registry = twitcher_service_factory(registry)
    db = mongodb(registry)
    catalog = MongodbCatalog(db.catalog, service_registry)
    return catalog


WPS_TYPE = "WPS"
THREDDS_TYPE = "THREDDS"
RESOURCE_TYPES = {
    WPS_TYPE: 'http://www.opengis.net/wps/1.0.0',
    THREDDS_TYPE: 'http://www.unidata.ucar.edu/namespaces/thredds/InvCatalog/v1.0'}


def _fetch_thredds_metadata(url, title=None):
    """Fetch capabilities metadata from thredds catalog service and return record dict."""
    # TODO: maybe use thredds siphon
    import threddsclient
    tds = threddsclient.read_url(url)
    title = title or tds.name or "Unknown"
    record = dict(
        type='service',
        title=title,
        abstract="",
        source=url,
        format=THREDDS_TYPE,
        creator='',
        keywords=['thredds'],
        rights='',
        # subjects = '',
        references=[])
    return record


def _fetch_wps_metadata(url, title=None):
    """Fetch capabilities metadata from wps service and return record dict."""
    wps = WebProcessingService(url, verify=False, skip_caps=False)
    record = dict(
        type='service',
        title=title or wps.identification.title or "Unknown",
        abstract=getattr(wps.identification, 'abstract', ''),
        source=wps.url,
        format=WPS_TYPE,
        creator=wps.provider.name,
        keywords=getattr(wps.identification, 'keywords', []),
        rights=getattr(wps.identification, 'accessconstraints', ''),
        # subjects = '',
        references=[])
    return record


class Catalog(object):
    def get_record_by_id(self, identifier):
        raise NotImplementedError

    def delete_record(self, identifier):
        raise NotImplementedError

    def insert_record(self, record):
        raise NotImplementedError

    def harvest(self, url, service_type, service_name=None, service_title=None, public=False, c4i=False):
        raise NotImplementedError

    def get_service_name(self, record):
        """Get service name from twitcher registry for given service (url)."""
        service = self.service_registry.get_service_by_url(record.source)
        if not service:
            raise Exception("Could not find service with url=%s", record.source)
        return service['name']

    def get_service_by_name(self, name):
        """Get service from twitcher registry by given service name."""
        return self.service_registry.get_service_by_name(name)

    def get_service_by_url(self, url):
        """Get service from twitcher registry by given url."""
        return self.service_registry.get_service_by_url(url)

    def get_services(self, service_type=None, maxrecords=100):
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

    def __init__(self, collection, service_registry):
        self.collection = collection
        self.service_registry = service_registry

    def get_record_by_id(self, identifier):
        return doc2record(self.collection.find_one({'identifier': identifier}))

    def delete_record(self, identifier):
        record = self.get_record_by_id(identifier)
        if record.format == WPS_TYPE:
            self.service_registry.unregister_service(self.get_service_name(record))
        self.collection.delete_one({'identifier': identifier})

    def insert_record(self, record):
        record['identifier'] = uuid.uuid4().hex
        self.collection.update_one({'source': record['source']}, {'$set': record}, True)

    def harvest(self, url, service_type, service_name=None, service_title=None, public=False, c4i=False):
        if service_type == THREDDS_TYPE:
            self.insert_record(_fetch_thredds_metadata(url, title=service_title))
        elif service_type == WPS_TYPE:
            # register service first
            service = self.service_registry.register_service(
                url=url,
                data={'name': service_name,
                      'public': public,
                      'c4i': c4i},
                overwrite=False)
            try:
                # fetch metadata
                record = _fetch_wps_metadata(service['url'], title=service_title)
                record['public'] = public
                self.insert_record(record)
            except Exception:
                LOGGER.exception("could not harvest metadata")
                self.service_registry.unregister_service(name=service_name)
                raise Exception("could not harvest metadata")
        else:
            raise NotImplementedError

    def get_services(self, service_type=None, maxrecords=100):
        search_filter = {'type': 'service'}
        if service_type:
            search_filter['format'] = service_type
        return [doc2record(doc) for doc in self.collection.find(search_filter)]

    def clear_services(self):
        self.service_registry.clear_services()
        self.collection.drop()
