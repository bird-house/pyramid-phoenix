from mako.template import Template
import uuid
from os.path import join, dirname
from collections import namedtuple

from owslib.csw import CatalogueServiceWeb
from owslib.fes import PropertyIsEqualTo, And
from owslib.wps import WebProcessingService

from twitcher.registry import service_registry_factory

from pyramid.settings import asbool
from pyramid.events import NewRequest

from phoenix.db import mongodb

import logging
logger = logging.getLogger(__name__)


def includeme(config):

    # catalog service
    def add_catalog(event):
        settings = event.request.registry.settings
        if settings.get('catalog') is None:
            try:
                settings['catalog'] = catalog_factory(config.registry)
            except:
                logger.exception('Could not connect catalog service.')
        else:
            logger.debug("catalog already initialized")
        event.request.catalog = settings.get('catalog')
    config.add_subscriber(add_catalog, NewRequest)


def catalog_factory(registry):
    settings = registry.settings

    service_registry = service_registry_factory(registry)

    if asbool(settings.get('phoenix.csw', True)):
        csw = CatalogueServiceWeb(url=settings['csw.url'], skip_caps=True)
        catalog = CatalogService(csw, service_registry)
    else:
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

    def harvest(self, url, service_type, service_name=None, service_title=None, public=False):
        raise NotImplementedError

    def get_service_by_url(self, url):
        # TODO: separate interface from abstract class
        return self.service_registry.get_service_by_url(url)

    def get_service_name(self, record):
        """Get service name from twitcher registry for given service (url)."""
        return self.get_service_name_by_url(record.source)

    def get_service_name_by_url(self, url):
        """Get service name from twitcher registry for given service (url)."""
        return self.service_registry.get_service_name(url)

    def get_services(self, service_type=None, maxrecords=100):
        raise NotImplementedError

    def clear_services(self):
        raise NotImplementedError

    
class CatalogService(Catalog):
    def __init__(self, csw, service_registry):
        self.csw = csw
        self.service_registry = service_registry

    def get_record_by_id(self, identifier):
        self.csw.getrecordbyid(id=[identifier])
        return self.csw.records[identifier]

    def delete_record(self, identifier):
        self.csw.transaction(ttype='delete', typename='csw:Record', identifier=identifier )

    def insert_record(self, record):
        record['identifier'] = uuid.uuid4().get_urn()
        templ_dc = Template(filename=join(dirname(__file__), "templates", "catalog", "dublin_core.xml"))
        self.csw.transaction(ttype="insert", typename='csw:Record', record=str(templ_dc.render(**record)))

    def harvest(self, url, service_type, service_name=None, service_title=None, public=False):
        if service_type == THREDDS_TYPE:
            self.insert_record(_fetch_thredds_metadata(url, service_title))
        else:  # ogc services
            self.service_registry.register_service(url=url, name=service_name, public=public)
            self.csw.harvest(source=url, resourcetype=RESOURCE_TYPES.get(service_type))

    def get_services(self, service_type=None, maxrecords=100):
        cs = PropertyIsEqualTo('dc:type', 'service')
        if service_type is not None:
            cs_format = PropertyIsEqualTo('dc:format', service_type)
            cs = And([cs, cs_format])
        self.csw.getrecords2(esn="full", constraints=[cs], maxrecords=maxrecords)
        return self.csw.records.values()


def doc2record(document):
    """Converts ``document`` from mongodb to a ``Record`` object."""
    record = None
    if isinstance(document, dict): 
        if '_id' in document:
            # _id field not allowed in record
            del document["_id"]
        record = namedtuple('Record', document.keys())(*document.values())
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
        record['identifier'] = uuid.uuid4().get_urn()
        self.collection.update_one({'source': record['source']}, {'$set': record}, True)

    def harvest(self, url, service_type, service_name=None, service_title=None, public=False):
        if service_type == THREDDS_TYPE:
            self.insert_record(_fetch_thredds_metadata(url, title=service_title))
        elif service_type == WPS_TYPE:
            # register service first
            service = self.service_registry.register_service(
                url=url, name=service_name, public=public, overwrite=False)
            # fetch metadata
            record = _fetch_wps_metadata(service['url'], title=service_title)
            record['public'] = public
            self.insert_record(record)
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






       


