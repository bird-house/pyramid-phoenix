# wpsschema.py
# Copyright (C) 2013 the ClimDaPs/Phoenix authors and contributors
# <see AUTHORS file>
#
# This module is part of ClimDaPs/Phoenix and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import colander
import deform
import deform_bootstrap_extra
import logging

import dateutil
import re
import urllib
import json

from owslib.wps import WebProcessingService

from .widget import TagsWidget
from .helpers import wps_url

__all__ = ['WPSSchema']

logger = logging.getLogger(__name__)

wps_registry = {}

@property
def RAW():
    return 'raw'

@property
def JSON():
    return 'json'

def get_wps(url):
    """
    Get wps instance with url. Using wps registry to cache wps instances.
    """
    global wps_registry
    logger.debug("get wps: %s", url)
    wps = wps_registry.get(url)
    if wps is None:
        logger.info('register new wps: %s', url)
        verbose = logger.isEnabledFor(logging.DEBUG)
        wps = WebProcessingService(url, verbose=verbose, skip_caps=True)
        logger.debug("loading wps caps ...")
        wps.getcapabilities()
        logger.debug("loading wps caps ... done")
        wps_registry[url] = wps
    logger.debug("number of registered wps: %d", len(wps_registry))
    logger.debug("get wps ... done")
    return wps

def build_request_url(service_url, identifier, inputs=[], output='output'):
    """
    Builds wps request url for direct raw output. Just one output parameter allowed.
    """
    req_url = service_url
    req_url += "?service=WPS&request=Execute&version=1.0.0"
    req_url += "&identifier=%s" % (identifier)
    data_inputs = ';'.join( map(lambda (key,value): "%s=%s" % (key, value), inputs ))
    req_url += "&DataInputs=%s" % (data_inputs)
    req_url += "&rawdataoutput=%s" % (output)
    req_url = req_url.encode('ascii', 'ignore')
    logger.debug('req url: %s', req_url)
    return req_url

def execute(url, format=RAW):
    result = None
    try:
        response = urllib.urlopen(url)
        if format == JSON:
            result = json.load(response)
        else:
            result = response.readlines()
    except Exception as e:
        log.error('wps execute failed! url=%s, err msg=%s' % (url, e.message()))
    return result

def execute_restflow(wps, nodes):
    import json
    nodes_json = json.dumps(nodes)

    # generate url for workflow description
    wf_url = wps.url
    wf_url += "?service=WPS&request=Execute&version=1.0.0&identifier=org.malleefowl.restflow.generate"
    wf_url += "&DataInputs=nodes=%s&rawdataoutput=output" % (nodes_json)
    wf_url = wf_url.encode('ascii', 'ignore')
    logger.debug('wf url: %s', wf_url)

    # run workflow
    identifier = 'org.malleefowl.restflow.run'
    inputs = [("workflow_description", wf_url)]
    outputs = [("output",True)]
    execution = wps.execute(identifier, inputs=inputs, output=outputs)

    return execution

def search_local_files(wps, openid, filter):
    req_url = wps.url
    req_url += "?service=WPS&request=Execute&version=1.0.0"
    req_url += "&identifier=org.malleefowl.listfiles" 
    req_url += "&DataInputs=openid=%s;filter=%s" % (openid, filter)
    req_url += "&rawdataoutput=output"
    req_url = req_url.encode('ascii', 'ignore')
    logger.debug('req url: %s', req_url)
    files = {}
    try:
        files = json.load(urllib.urlopen(req_url))
    except Exception as e:
        logger.error('retrieving files failed! openid=%s, filter=%s, error msg=%s' % (openid, filter, e.message))
    return files

# Memory tempstore for file uploads
# ---------------------------------

class MemoryTmpStore(dict):
    """ Instances of this class implement the
    :class:`deform.interfaces.FileUploadTempStore` interface"""
    def preview_url(self, uid):
        return None

tmpstore = MemoryTmpStore()


# wps input schema
# ----------------

class WPSSchema(colander.SchemaNode):
    """ Build a Colander Schema based on the WPS data inputs.

    This Schema generator is based on:
    http://colanderalchemy.readthedocs.org/en/latest/

    TODO: use widget category as grouping info
    TODO: fix dataType in wps client
    TODO: use insert_before, add_before, insert etc for ordering of elements
    """

    appstruct = {}

    def __init__(self, info=False, process=None, unknown='ignore', **kw):
        """ Initialise the given mapped schema according to options provided.

        Arguments/Keywords

        info:
           Add info fields for notes and tags (boolean).

           Default: False

        process
           An ``WPS`` process description that you want a ``Colander`` schema
           to be generated for.

        unknown
           Represents the `unknown` argument passed to
           :class:`colander.Mapping`.

           From Colander:

           ``unknown`` controls the behavior of this type when an unknown
           key is encountered in the cstruct passed to the deserialize
           method of this instance.

           Default: 'ignore'
        \*\*kw
           Represents *all* other options able to be passed to a
           :class:`colander.SchemaNode`. Keywords passed will influence the
           resulting mapped schema accordingly (for instance, passing
           ``title='My Model'`` means the returned schema will have its
           ``title`` attribute set accordingly.

           See http://docs.pylonsproject.org/projects/colander/en/latest/basics.html for more information.
        """

        kwargs = kw.copy()

        # The default type of this SchemaNode is Mapping.
        colander.SchemaNode.__init__(self, colander.Mapping(unknown), **kwargs)
        self.info = info
        self.process = process
        self.unknown = unknown
        self.kwargs = kwargs or {}   

        if info:
            self.add_info_nodes()
        self.add_nodes(process)

    def add_info_nodes(self):
        #logger.debug("adding info nodes")
        
        node = colander.SchemaNode(
            colander.String(),
            name = 'info_notes',
            title = 'Notes',
            description = 'Enter some notes for your process',
            default = 'test',
            missing = 'test',
            validator = colander.Length(max=150),
            widget = deform.widget.TextAreaWidget(rows=2, cols=80),
            )
        self.add(node)

        node = colander.SchemaNode(
            colander.String(),
            name = 'info_tags',
            title = 'Tags',
            description = 'Enter some tags',
            default = 'test',
            missing = 'test',
            widget = TagsWidget()
            )
        self.add(node)
        
    def add_nodes(self, process):
        if process is None:
            return

        logger.debug("adding nodes for process inputs, num inputs = %s", len(process.dataInputs))

        for data_input in process.dataInputs:
            node = None

            if data_input.dataType == None:
                node = self.boundingbox(data_input) 
            elif 'www.w3.org' in data_input.dataType:
                node = self.literal_data(data_input)
            elif 'ComplexData' in data_input.dataType:
                node = self.complex_data(data_input)
            else:
                raise Exception('unknown data type %s' % (data_input.dataType))

            if node is None:
                continue

            self.add(node)

    def literal_data(self, data_input):
        node = colander.SchemaNode(
            self.colander_literal_type(data_input),
            name = data_input.identifier,
            title = data_input.title,
            )

        # sometimes abstract is not set
        if hasattr(data_input, 'abstract'):
            node.description = data_input.abstract
        # optional value?
        if data_input.minOccurs == 0:
            node.missing = colander.drop
        # TODO: fix init of default
        if hasattr(data_input, 'defaultValue'):
            if type(node.typ) == colander.DateTime:
                #logger.debug('we have a datetime default value')
                node.default = dateutil.parser.parse(data_input.defaultValue)
            else:
                node.default = data_input.defaultValue
        self.colander_literal_widget(node, data_input)

        # sequence of nodes ...
        if data_input.maxOccurs > 1:
            node = colander.SchemaNode(
                colander.Sequence(), 
                node,
                name=data_input.identifier,
                title=data_input.title,
                validator=colander.Length(max=data_input.maxOccurs)
                )

        return node

    def colander_literal_type(self, data_input):
        #logger.debug('data input type = %s', data_input.dataType)
        if 'boolean' in data_input.dataType:
            return colander.Boolean()
        elif 'integer' in data_input.dataType:
            return colander.Integer()
        elif 'float' in data_input.dataType:
            return colander.Float()
        elif 'double' in data_input.dataType:
            return colander.Float()
        elif 'decimal' in data_input.dataType:
            return colander.Decimal()
        elif 'string' in data_input.dataType:
            return colander.String()
        elif 'dateTime' in data_input.dataType:
            return colander.DateTime()
        elif 'date' in data_input.dataType:
            return colander.Date()
        elif 'time' in data_input.dataType:
            return colander.Time()
        elif 'duration' in data_input.dataType:
            # TODO: check correct type
            # http://www.w3.org/TR/xmlschema-2/#duration
            return colander.Time()
        # guessing from default
        elif hasattr(data_input, 'defaultValue'):
            try:
                dt = dateutil.parser.parse(data_input.defaultValue)
            except:
                return colander.String()
            else:
                return colander.DateTime()
        else:
            return colander.String()

    def colander_literal_widget(self, node, data_input):
        if len(data_input.allowedValues) > 0 and not 'AnyValue' in data_input.allowedValues:
            #logger.debug('allowed values %s', data_input.allowedValues)
            choices = []
            for value in data_input.allowedValues:
                choices.append([value, value])
                #logger.debug('using select widget for %s', data_input.identifier)
            node.widget = deform.widget.SelectWidget(values=choices)
        elif type(node.typ) == colander.DateTime:
            #logger.debug('using datetime widget for %s', data_input.identifier)
            node.widget = deform.widget.DateInputWidget()
        elif type(node.typ) == colander.Boolean:
            #logger.debug('using checkbox widget for %s', data_input.identifier)
            node.widget = deform.widget.CheckboxWidget()
        elif 'password' in data_input.identifier:
            #logger.debug('using password widget for %s', data_input.identifier)
            node.widget = deform.widget.PasswordWidget(size=20)
        else:
            #logger.debug('using text widget for %s', data_input.identifier)
            node.widget = deform.widget.TextInputWidget()

        logger.debug("choosen widget, identifier=%s, widget=%s", data_input.identifier, node.widget)

    def complex_data(self, data_input):
        # TODO: handle upload, url, direct input for complex data

        node_upload = colander.SchemaNode(
            deform.FileData(),
            name=data_input.identifier,
            title=data_input.title,
            widget=deform.widget.FileUploadWidget(tmpstore)
            )
        node_url = colander.SchemaNode(
            colander.String(),
            name = data_input.identifier,
            title = data_input.title,
            widget = deform.widget.TextInputWidget(),
            validator = colander.url)

        node = node_url

        # sometimes abstract is not set
        if hasattr(data_input, 'abstract'):
            node.description = data_input.abstract

        # optional value?
        if data_input.minOccurs == 0:
            node.missing = colander.drop

        # finally add node to root schema
        # sequence of nodes ...
        if data_input.maxOccurs > 1:
            node = colander.SchemaNode(
                colander.Sequence(), 
                node,
                name=data_input.identifier,
                title=data_input.title,
                validator=colander.Length(max=data_input.maxOccurs)
                )
        
        return node

    def boundingbox(self, data_input):
        node = colander.SchemaNode(
            colander.String(),
            name=data_input.identifier,
            title=data_input.title,
            default="0,-90,180,90",
            widget=deform.widget.TextInputWidget()
            )
        # sometimes abstract is not set
        if hasattr(data_input, 'abstract'):
            node.description = data_input.abstract

        # optional value?
        if data_input.minOccurs == 0:
            node.missing = colander.drop

        # validator
        pattern = '-?\d+,-?\d+,-?\d+,-?\d+'
        regex = re.compile(pattern)
        node.validator = colander.Regex(
            regex=regex, 
            msg='String does not match pattern: minx,miny,maxx,maxy')

        # finally add node to root schema
        # sequence of nodes ...
        if data_input.maxOccurs > 1:
            node = colander.SchemaNode(
                colander.Sequence(), 
                node,
                name=data_input.identifier,
                title=data_input.title,
                validator=colander.Length(max=data_input.maxOccurs)
                )
        
        return node

    def bind(self, **kw):
        cloned = self.clone()
        cloned._bind(kw)

        logger.debug('after bind: num schema children = %s', len(cloned.children))
        return cloned

    def clone(self):
        cloned = self.__class__(
            self.info,
            self.process,
            self.unknown,
            **self.kwargs)
        cloned.__dict__.update(self.__dict__)
        cloned.children = [node.clone() for node in self.children]
        return cloned
        
    
