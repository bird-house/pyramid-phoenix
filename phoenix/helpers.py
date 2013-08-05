import types

from pyesgf.search import SearchConnection

import logging

log = logging.getLogger(__name__)

def wps_url(request):
    settings = request.registry.settings
    # TODO: dont use hard coded project name
    service_url = settings.get('phoenix.wps', None)
    log.debug('using wps = %s', service_url)
    return service_url

def update_wps_url(request, wps_url):
    settings = request.registry.settings
    settings['phoenix.wps'] = wps_url
   
def csw_url(request):
    settings = request.registry.settings
    # TODO: dont use hard coded project name
    service_url = settings.get('phoenix.csw', None)
    log.debug('using csw = %s', service_url)
    return service_url

def esgsearch_url(request):
    settings = request.registry.settings
    # TODO: dont use hard coded project name
    service_url = settings.get('esgf.search', None)
    log.debug('using esgf seach = %s', service_url)
    return service_url

def whitelist(request):
	settings = request.registry.settings
	whitelist_str = settings.get('phoenix.login.whitelist', '')
	whitelist = whitelist_str.split(',')
	return whitelist

def mongodb_conn(request):
	settings = request.registry.settings
	conn = settings.get('mongodb_conn', None)
	return conn

def is_url(text):
    """Check wheather given text is url or not

    TODO: code is taken from pywps. Maybe there is a better alternative.
    """
        
    try:
        (urltype, opaquestring) = urllib.splittype(text)

        if urltype in ["http","https","ftp"]:
            return True
        else:
            return False
    except:
        return False

def esgf_search_conn(request):
    return SearchConnection(esgsearch_url(request), distrib=False)
    
def esgf_search_context(request):
    conn = esgf_search_conn(request)
    ctx = conn.new_context(
        project='CMIP5', product='output1', 
        replica=False, latest=True)
    return ctx

def execute_wps(wps, identifier, params):
    # TODO: handle sync/async case, 
    # TODO: fix wps-client (parsing response)
    # TODO: fix wps-client for store/status setting or use own xml template

    log.debug('execute wps process')

    process = wps.describeprocess(identifier)

    input_types = {}
    for data_input in process.dataInputs:
        input_types[data_input.identifier] = data_input.dataType
 
    inputs = []
    # TODO: dont append value if default
    for (key, value) in params.iteritems():
        values = []
        # TODO: how do i handle serveral values in wps?
        if type(value) == types.ListType:
            values = value
        else:
            values = [value]

        # there might be more than one value (maxOccurs > 1)
        for value in values:
            # bbox
            if input_types[key] == None:
                # TODO: handle bounding box
                log.debug('bbox value: %s' % value)
                inputs.append( (key, str(value)) )
                # if len(value) > 0:
                #     (minx, miny, maxx, maxy) = value[0].split(',')
                #     bbox = [[float(minx),float(miny)],[float(maxx),float(maxy)]]
                #     inputs.append( (key, str(bbox)) )
                # else:
                #     inputs.append( (key, str(value)) )
            # complex data
            elif input_types[key] == 'ComplexData':
                # TODO: handle complex data
                log.debug('complex value: %s' % value)
                if is_url(value):
                    inputs.append( (key, value) )
                elif type(value) == type({}):
                    if value.has_key('fp'):
                        str_value = value.get('fp').read()
                        inputs.append( (key, str_value) )
                else:
                    inputs.append( (key, str(value) ))
            else:
                inputs.append( (key, str(value)) )

    log.debug('inputs =  %s', inputs)

    outputs = []
    for output in process.processOutputs:
        outputs.append( (output.identifier, output.dataType == 'ComplexData' ) )

    execution = wps.execute(identifier, inputs=inputs, output=outputs)
 
    log.debug('status_location = %s', execution.statusLocation)

    return execution


