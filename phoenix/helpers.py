# schema.py
# Copyright (C) 2013 the ClimDaPs/Phoenix authors and contributors
# <see AUTHORS file>
#
# This module is part of ClimDaPs/Phoenix and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import types
import markupsafe
from pyramid.security import authenticated_userid
import logging

log = logging.getLogger(__name__)

SIGNIN_HTML = '<a href="/login">Login</a>'
SIGNOUT_HTML = '<a href="/logout" id="signout">Logout</a>'

def button(request):
    """If the user is logged in, returns the logout button, otherwise returns the login button"""
    if not authenticated_userid(request):
        return markupsafe.Markup(SIGNIN_HTML)
    else:
        return markupsafe.Markup(SIGNOUT_HTML)

def get_setting(request, key):
    settings = request.registry.settings
    value = settings.get(key, None)
    return value

def set_setting(request, key, value):
    settings = request.registry.settings
    settings[key] = value

def supervisor_url(request):
    return get_setting(request, 'phoenix.supervisor')

def wps_url(request):
    return get_setting(request, 'phoenix.wps')

def update_wps_url(request, wps_url):
    set_setting(request, 'phoenix.wps', wps_url)
   
def csw_url(request):
    return get_setting(request, 'phoenix.csw')

def thredds_url(request):
    return get_setting(request, 'phoenix.thredds')
   
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


