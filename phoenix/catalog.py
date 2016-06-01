from mako.template import Template
import uuid
from urlparse import urlparse
from os.path import join, dirname

from owslib.csw import CatalogueServiceWeb
from owslib.fes import PropertyIsEqualTo, And
from twitcher.registry import service_registry_factory, proxy_url

from pyramid.settings import asbool
from pyramid.events import NewRequest

from phoenix.db import mongodb

import logging
logger = logging.getLogger(__name__)

def includeme(config):
    settings = config.registry.settings

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
    catalog = None

    if asbool(settings.get('phoenix.csw', True)):
        csw = CatalogueServiceWeb(url=settings['csw.url'])
        catalog = CatalogService(csw)
    else:
        db = mongodb(registry)
        catalog = MongodbCatalog(db.catalog)
    return catalog

WPS_TYPE = "WPS"
THREDDS_TYPE = "THREDDS"

def wps_url(request, identifier):
    record = request.catalog.get_record_by_id(identifier)
    # TODO: fix service name
    service_name = record.title.lower()
    service_registry = service_registry_factory(request.registry)
    service_registry.register_service(name=service_name, url=record.source)
    url = proxy_url(request, service_name)
    logger.debug("identifier=%s, source=%s, url=%s", identifier, record.source, url)
    return url

def wps_id(request, service_name):
    service = request.catalog.get_service_by_name(service_name)
    if service is not None:
        return service.identifier
    return None

class Catalog(object):
    def get_record_by_id(self, identifier):
        raise NotImplementedError

    def delete_record(self, identifier):
        raise NotImplementedError

    def insert_record(self, record):
        raise NotImplementedError

    def harvest(self, url, service_type, service_name=None):
        raise NotImplementedError

    def get_services(self, service_type=None, maxrecords=100):
        raise NotImplementedError

    def get_service_by_name(self, service_name, service_type=WPS_TYPE):
        raise NotImplementedError
    
class CatalogService(Catalog):
    def __init__(self, csw):
        self.csw = csw

    def get_record_by_id(self, identifier):
        self.csw.getrecordbyid(id=[identifier])
        return self.csw.records[identifier]

    def delete_record(self, identifier):
        self.csw.transaction(ttype='delete', typename='csw:Record', identifier=identifier )

    def insert_record(self, record):
        record['identifier'] = uuid.uuid4().get_urn()
        templ_dc = Template(filename=join(dirname(__file__), "templates", "catalog", "dublin_core.xml"))
        self.csw.transaction(ttype="insert", typename='csw:Record', record=str(templ_dc.render(**record)))

    def harvest(self, url, service_type, service_name=None):
        if service_type == THREDDS_TYPE:
            import threddsclient
            tds = threddsclient.read_url(url)
            title = tds.name
            if service_name and len(service_name.strip()) > 2:
                title = service_name
            elif len(title.strip()) == 0:
                title = url
            record = dict(
                type = 'service',
                title = title,
                abstract = "",
                source = url,
                format = THREDDS_TYPE,
                creator = '',
                keywords = 'thredds',
                rights = '')
            self.insert_record(record)
        else: # ogc services
            self.csw.harvest(source=url, resourcetype=service_type)

    def get_services(self, service_type=None, maxrecords=100):
        cs = PropertyIsEqualTo('dc:type', 'service')
        if service_type is not None:
            cs_format = PropertyIsEqualTo('dc:format', service_type)
            cs = And([cs, cs_format])
        self.csw.getrecords2(esn="full", constraints=[cs], maxrecords=maxrecords)
        return self.csw.records.values()

    def get_service_by_name(self, service_name, service_type=WPS_TYPE):
        cs_type = PropertyIsEqualTo('dc:type', 'service')
        cs_format = PropertyIsEqualTo('dc:format', service_type)
        cs_title = PropertyIsEqualTo('dc:title', service_name)
        cs = And([cs_type, cs_format, cs_title])
        self.csw.getrecords2(esn="full", constraints=[cs], maxrecords=1)
        service = None
        if self.csw.results['returned'] == 1:
            service = self.csw.records.values()[0]
        return service
        

class MongodbCatalog(Catalog):
    def __init__(self, collection):
        self.collection = collection




       


