from mako.template import Template
import uuid
from urlparse import urlparse
from os.path import join, dirname

from owslib.fes import PropertyIsEqualTo

from twitcher.registry import service_registry_factory, proxy_url

import logging
logger = logging.getLogger(__name__)


def wps_id(request, url):
    # TODO: fix retrieval of wps id
    from owslib.wps import WebProcessingService
    logger.debug("wps url %s", url)
    wps = WebProcessingService(url=url, verify=False)
    #wps_query = PropertyIsEqualTo('dc:format', 'WPS')
    title_query = PropertyIsEqualTo('dc:title', wps.identification.title)
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

def wps_caps_url(request, identifier):
    parsed = urlparse( wps_url(request, identifier) )
    caps_url = "%s://%s%s?service=WPS&request=GetCapabilities" % (parsed.scheme, parsed.netloc, parsed.path)
    return caps_url

def wps_describe_url(request, url, processid):
    parsed = urlparse(url)
    desc_url = "{0}://{1}{2}?service=WPS&version=1.0.0&request=DescribeProcess&identifier={3}".format(
        parsed.scheme, parsed.netloc, parsed.path, processid)
    return desc_url

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
    templ_dc = Template(filename=join(dirname(__file__), "templates", "dublin_core.xml"))
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


       


