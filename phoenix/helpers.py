import types
import uuid
import datetime

from pyesgf.search import SearchConnection

import logging

log = logging.getLogger(__name__)

def get_setting(request, key):
    settings = request.registry.settings
    value = settings.get(key, None)
    return value

def set_setting(request, key, value):
    settings = request.registry.settings
    settings[key] = value

def wps_url(request):
    return get_setting(request, 'phoenix.wps')

def update_wps_url(request, wps_url):
    set_setting(request, 'phoenix.wps', wps_url)
   
def csw_url(request):
    return get_setting(request, 'phoenix.csw')
   
def esgsearch_url(request):
    return get_setting(request, 'esgf.search')

def whitelist(request):
    return get_setting(request, 'phoenix.login.whitelist')

def mongodb_conn(request):
    return get_setting(request, 'mongodb_conn')

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

def mongodb_add_job(request, user_id, identifier, wps_url, execution):
    conn = mongodb_conn(request)
    conn.phoenix_db.history.save(dict(
        user_id= user_id, 
        uuid=uuid.uuid4().get_hex(),
        identifier=identifier,
        service_url=wps_url,
        status_location=execution.statusLocation,
        status = execution.status,
        start_time = datetime.datetime.now(),
        end_time = datetime.datetime.now(),
      ))

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


