from mako.template import Template
import uuid

def wps_url(request, identifier):
    return get_wps(request, identifier).source

def wps_caps_url(request, identifier):
    wps = get_wps(request, identifier)
    for ref in wps.references:
        if 'get-capabilities' in ref.get('scheme'):
            return ref.get('url')
    return None

def get_wps(request, identifier):
    csw = request.csw
    csw.getrecordbyid(id=[identifier])
    return csw.records[identifier]
    
def get_wps_list(request):
    csw = request.csw
    from owslib.fes import PropertyIsEqualTo
    wps_query = PropertyIsEqualTo('dc:format', 'WPS')
    csw.getrecords2(esn="full", constraints=[wps_query], maxrecords=100)
    return csw.records.values()

def get_thredds_list(request):
    csw = request.csw
    from owslib.fes import PropertyIsEqualTo
    wps_query = PropertyIsEqualTo('dc:format', 'THREDDS')
    csw.getrecords2(esn="full", constraints=[wps_query], maxrecords=100)
    return csw.records.values()

def publish(request, record):
    from os.path import join, dirname
   
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


