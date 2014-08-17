import types
import urllib2

import logging
logger = logging.getLogger(__name__)

def quote_wps_params(params):
    return map(lambda(item): ( item[0], urllib2.quote(str(item[1])).decode('utf8') ), params)

def unquote_wps_params(params):
    return map(lambda(item): ( item[0], urllib2.unquote(item[1]) ), params)

def is_url(text):
    """Check wheather given text is url or not

    TODO: code is taken from pywps. Maybe there is a better alternative.
    """
    logger.debug("check is_url, text=%s", text)
        
    try:
        (urltype, opaquestring) = urllib2.splittype(text)
        logger.debug('urltype=%s, str=%s', urltype, opaquestring)

        if urltype in ["http","https","ftp"]:
            return True
        else:
            return False
    except Exception as e:
        logger.error('error occured in is_url, error=%s', e.message)
        return False

def execute_wps(wps, identifier, params):
    # TODO: handle sync/async case, 
    # TODO: fix wps-client (parsing response)
    # TODO: fix wps-client for store/status setting or use own xml template

    logger.debug('execute wps process')

    process = wps.describeprocess(identifier)

    input_types = {}
    mime_types = {}
    for data_input in process.dataInputs:
        input_types[data_input.identifier] = data_input.dataType
        mime_types[data_input.identifier] = map(lambda val: val.mimeType, data_input.supportedValues)
 
    inputs = []
    # TODO: dont append value if default
    for (key, value) in params.iteritems():
        # ignore info params
        if 'keywords' in key:
            continue
        if 'abstract' in key:
            continue
        
        values = []
        # TODO: how do i handle serveral values in wps?
        if type(value) == types.ListType:
            values = value
        else:
            values = [value]

        # there might be more than one value (maxOccurs > 1)
        for value in values:
            logger.debug('handling value %s, type=%s', value, type(value))
            # bbox
            if input_types[key] == None:
                # TODO: handle bounding box
                logger.debug('bbox value: %s' % value)
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
                logger.debug('complex value')
                if is_url(value):
                    logger.debug('is url')
                    inputs.append( (key, str(value)) )
                else:
                    logger.debug('is upload')
                    try:
                        if value.has_key('fp'):
                            content = value.get('fp').read()
                            # TODO: fix mime-type encoding
                            if 'application/x-netcdf' in mime_types[key]:
                                import base64
                                logger.debug('encode content of %s', key)
                                content =  base64.encodestring(content)
                            inputs.append( (key, content) )
                    except:
                        logger.error('could not add complex value')
            else:
                inputs.append( (key, str(value)) )

    logger.debug('num inputs =  %s', len(inputs))

    outputs = []
    for output in process.processOutputs:
        outputs.append( (output.identifier, output.dataType == 'ComplexData' ) )

    execution = wps.execute(identifier, inputs=inputs, output=outputs)
    logger.debug('status_location = %s', execution.statusLocation)

    return execution


