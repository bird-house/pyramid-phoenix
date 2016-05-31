from mako.template import Template
import uuid
from urlparse import urlparse
from os.path import join, dirname

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
    if asbool(settings.get('phoenix.csw', True)):
        logger.info('Add catalog')
        
        def add_csw(event):
            settings = event.request.registry.settings
            if settings.get('csw') is None:
                try:
                    from owslib.csw import CatalogueServiceWeb
                    settings['csw'] = CatalogueServiceWeb(url=settings['csw.url'])
                    logger.debug("init csw")
                except:
                    logger.exception('Could not connect catalog service %s', settings['csw.url'])
            else:
                logger.debug("csw already initialized")
            event.request.csw = settings.get('csw')
        config.add_subscriber(add_csw, NewRequest)

    # check if csw is activated
    def csw_activated(request):
        settings = request.registry.settings
        return asbool(settings.get('phoenix.csw', True))
    config.add_request_method(csw_activated, reify=True)

def catalog_factory(registry):
    settings = registry.settings
    catalog = None
    service_registry = service_registry_factory(registry)
    if asbool(settings.get('phoenix.csw', True)):
        catalog = CatalogService(settings.get('csw'), service_registry)
    else:
        db = mongodb(registry)
        catalog = MongodbAccessTokenStore(db.catalog)
    return catalog

class Catalog(object):
    def wps_id(self, name):
        raise NotImplementedError

    def wps_url(self, request, identifier):
        raise NotImplementedError

    def get_wps_list(self):
        raise NotImplementedError

    def get_thredds_list(self):
        raise NotImplementedError

    def publish(self, record):
        raise NotImplementedError

    def harvest_service(self, url, service_type, service_name=None):
        raise NotImplementedError
    
class CatalogService(Catalog):
    def __init__(self, csw, service_registry):
        self.csw = csw
        self.service_registry = service_registry

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
        self.csw.getrecordbyid(id=[identifier])
        record = self.csw.records[identifier]
        # TODO: fix service name
        service_name = record.title.lower()
        self.service_registry.register_service(name=service_name, url=record.source)
        url = proxy_url(request, service_name)
        logger.debug("identifier=%s, source=%s, url=%s", identifier, record.source, url)
        return url

    def get_wps_list(self):
        wps_query = PropertyIsEqualTo('dc:format', 'WPS')
        self.csw.getrecords2(esn="full", constraints=[wps_query], maxrecords=100)
        return self.csw.records.values()

class MongodbCatalog(Catalog):
    def __init__(self, collection):
        self.collection = collection

def wps_id(request, name):
    # TODO: fix retrieval of wps id
    #wps_query = PropertyIsEqualTo('dc:format', 'WPS')
    title_query = PropertyIsEqualTo('dc:title', name)
    request.csw.getrecords2(esn="full", constraints=[title_query], maxrecords=1)
    logger.debug("csw results %s", request.csw.results)
    identifier = None
    if len(request.csw.records.values()) == 1:
        rec = request.csw.records.values()[0]
        identifier = rec.identifier
        logger.debug("found rec %s %s %s", rec.identifier, rec.title, rec.source)
    return identifier

def wps_url(request, identifier):
    request.csw.getrecordbyid(id=[identifier])
    record = request.csw.records[identifier]
    registry = service_registry_factory(request.registry)
    # TODO: fix service name
    service_name = record.title.lower()
    registry.register_service(name=service_name, url=record.source)
    url = proxy_url(request, service_name)
    logger.debug("identifier=%s, source=%s, url=%s", identifier, record.source, url)
    return url

def get_wps_list(request):
    wps_query = PropertyIsEqualTo('dc:format', 'WPS')
    request.csw.getrecords2(esn="full", constraints=[wps_query], maxrecords=100)
    return request.csw.records.values()

def get_thredds_list(request):
    wps_query = PropertyIsEqualTo('dc:format', 'THREDDS')
    request.csw.getrecords2(esn="full", constraints=[wps_query], maxrecords=100)
    return request.csw.records.values()

def publish(request, record):
    record['identifier'] = uuid.uuid4().get_urn()
    templ_dc = Template(filename=join(dirname(__file__), "templates", "catalog", "dublin_core.xml"))
    request.csw.transaction(ttype="insert", typename='csw:Record', record=str(templ_dc.render(**record)))

def harvest_service(request, url, service_type, service_name=None):
    if service_type == 'thredds_catalog':
        import threddsclient
        tds = threddsclient.read_url(url)
        title = tds.name
        if service_name and len(service_name.strip()) > 2:
            title = service_name
        elif len(title.strip()) == 0:
            title = url
        record = dict(
            title = title,
            abstract = "",
            source = url,
            format = "THREDDS",
            creator = '',
            keywords = 'thredds',
            rights = '')
        publish(request, record)
    else: # ogc services
        request.csw.harvest(source=url, resourcetype=service_type)


       


