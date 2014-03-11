# schema.py
# Copyright (C) 2013 the ClimDaPs/Phoenix authors and contributors
# <see AUTHORS file>
#
# This module is part of ClimDaPs/Phoenix and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import types
import markupsafe
import urllib2
from pyramid.security import authenticated_userid

import logging
logger = logging.getLogger(__name__)

SIGNIN_HTML = '<a href="/signin"><i class="icon-user"></i> Sign in</a>'
SIGNOUT_HTML = '<a href="/logout" id="signout" title="Logout %s"><i class="icon-off"></i> Sign out</a>'

def button(request):
    """If the user is logged in, returns the logout button, otherwise returns the login button"""
    if not authenticated_userid(request):
        return markupsafe.Markup(SIGNIN_HTML)
    else:
        return markupsafe.Markup(SIGNOUT_HTML) % (authenticated_userid(request))

def quote_wps_params(params):
    return map(lambda(item): ( item[0], urllib2.quote(str(item[1])).decode('utf8') ), params)

def unquote_wps_params(params):
    return map(lambda(item): ( item[0], urllib2.unquote(item[1]) ), params)

def get_setting(request, key):
    settings = request.registry.settings
    value = settings.get(key, None)
    logger.debug('get_setting(): key=%s, value=%s' % (key, value))
    return value

def set_setting(request, key, value):
    settings = request.registry.settings
    settings[key] = value

def supervisor_url(request):
    return get_setting(request, 'phoenix.supervisor')

def wps_url(request):
    url = get_setting(request, 'malleefowl.wps')
    return url

def thredds_url(request):
    return get_setting(request, 'phoenix.thredds')
   
def esgsearch_url(request):
    return get_setting(request, 'esgf.search')

def admin_users(request):
    value = get_setting(request, 'phoenix.admin_users')
    if value:
        import re
        return map(str.strip, re.split("\\s+", value.strip()))
    return []

def mongodb_conn(request):
    return get_setting(request, 'mongodb_conn')

def sys_token(request):
    return get_setting(request, 'malleefowl.sys_token')

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

def execute_wps(wps, identifier, params):
    # TODO: handle sync/async case, 
    # TODO: fix wps-client (parsing response)
    # TODO: fix wps-client for store/status setting or use own xml template

    logger.debug('execute wps process')

    process = wps.describeprocess(identifier)

    input_types = {}
    for data_input in process.dataInputs:
        input_types[data_input.identifier] = data_input.dataType
 
    inputs = []
    # TODO: dont append value if default
    for (key, value) in params.iteritems():
        # ignore info params
        if 'info_tags' in key:
            continue
        if 'info_notes' in key:
            continue
        
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
                logger.debug('complex value: %s' % value)
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

    logger.debug('inputs =  %s', inputs)

    outputs = []
    for output in process.processOutputs:
        outputs.append( (output.identifier, output.dataType == 'ComplexData' ) )

    execution = wps.execute(identifier, inputs=inputs, output=outputs)
 
    logger.debug('status_location = %s', execution.statusLocation)

    return execution


