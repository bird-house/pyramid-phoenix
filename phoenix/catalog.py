from mako.template import Template
import uuid
from urlparse import urlparse
from os.path import join, dirname

from owslib.csw import CatalogueServiceWeb
from owslib.fes import PropertyIsEqualTo
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
    service_registry = service_registry_factory(registry)
    if asbool(settings.get('phoenix.csw', True)):
        csw = CatalogueServiceWeb(url=settings['csw.url'])
        catalog = CatalogService(csw, service_registry)
    else:
        db = mongodb(registry)
        catalog = MongodbCatalog(db.catalog)
    return catalog

class Catalog(object):
    def get_record_by_id(self, identifier):
        raise NotImplementedError

    def delete_record(self, identifier):
        raise NotImplementedError

    def insert_record(self, record):
        raise NotImplementedError

    def harvest(self, url, service_type, service_name=None):
        raise NotImplementedError

    def get_services(self, maxrecords=100):
        raise NotImplementedError
    
    def wps_id(self, name):
        raise NotImplementedError

    def wps_url(self, request, identifier):
        raise NotImplementedError
    
    def get_wps_list(self):
        raise NotImplementedError

    def get_thredds_list(self):
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

    def harvest(self, url, service_type, service_name=None):
        if service_type == 'thredds_catalog':
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
                format = "THREDDS",
                creator = '',
                keywords = 'thredds',
                rights = '')
            self.insert_record(record)
        else: # ogc services
            self.csw.harvest(source=url, resourcetype=service_type)

    def get_services(self, maxrecords=100):
        query = PropertyIsEqualTo('dc:type', 'service')
        self.csw.getrecords2(esn="full", constraints=[query], maxrecords=maxrecords)
        return self.csw.records.values()

    def wps_id(self, name):
        # TODO: fix retrieval of wps id
        #wps_query = PropertyIsEqualTo('dc:format', 'WPS')
        title_query = PropertyIsEqualTo('dc:title', name)
        self.csw.getrecords2(esn="full", constraints=[title_query], maxrecords=1)
        logger.debug("csw results %s", self.csw.results)
        identifier = None
        if len(self.csw.records.values()) == 1:
            rec = self.csw.records.values()[0]
            identifier = rec.identifier
            logger.debug("found rec %s %s %s", rec.identifier, rec.title, rec.source)
        return identifier

    def wps_url(self, request, identifier):
        record = self.get_record_by_id(identifier)
        # TODO: fix service name
        service_name = record.title.lower()
        self.service_registry.register_service(name=service_name, url=record.source)
        url = proxy_url(request, service_name)
        logger.debug("identifier=%s, source=%s, url=%s", identifier, record.source, url)
        return url

    def get_wps_list(self):
        query = PropertyIsEqualTo('dc:format', 'WPS')
        self.csw.getrecords2(esn="full", constraints=[query], maxrecords=100)
        return self.csw.records.values()

    def get_thredds_list(self):
        query = PropertyIsEqualTo('dc:format', 'THREDDS')
        self.csw.getrecords2(esn="full", constraints=[query], maxrecords=100)
        return self.csw.records.values()

   

class MongodbCatalog(Catalog):
    def __init__(self, collection):
        self.collection = collection




       


