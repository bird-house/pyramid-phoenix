import colander
import deform
import logging

import dateutil
import re
import urllib
import json
import types

from owslib.wps import WebProcessingService, monitorExecution

from .widget import TagsWidget

__all__ = ['WPSSchema']

logger = logging.getLogger(__name__)

@property
def RAW():
    return 'raw'

@property
def JSON():
    return 'json'

def build_request_url(service_url, identifier, inputs=[], output='output'):
    """
    Builds wps request url for direct raw output. Just one output parameter allowed.
    """
    req_url = service_url
    req_url += "?service=WPS&request=Execute&version=1.0.0"
    req_url += "&identifier=%s" % (identifier)
    data_inputs = ';'.join( map(lambda (key,value): "%s=%s" % (key, value), inputs ))
    req_url += "&DataInputs=%s" % (data_inputs)
    if output is not None:
        req_url += "&rawdataoutput=%s" % (output)
    req_url = req_url.encode('ascii', 'ignore')
    logger.debug('req url: %s', req_url)
    return req_url

def execute_with_url(url, format=RAW):
    result = None
    try:
        response = urllib.urlopen(url)
        if format == JSON:
            result = json.load(response)
        else:
            result = response.readlines()
    except Exception as e:
        logger.error('wps execute failed! url=%s, err msg=%s' % (url, e.message))
    return result

def execute(service_url, identifier, inputs=[], output='output', format=RAW):
    result = None
    
    try:
        logger.debug("execute wps ... ")
        req_url = build_request_url(service_url,
                                    identifier=identifier,
                                    inputs=inputs,
                                    output=output)
        result = execute_with_url(req_url, format=format)
        logger.debug("execute wps ... done")
    except Exception as e:
        logger.error('execute wps ... failed, error msg=%s' % (e.message))
        raise
    return result

def gen_token(wps, sys_token, userid):
    # TODO: need token exception if not avail
    token = None
    try:
        execution = wps.execute(
            identifier='org.malleefowl.token.generate',
            inputs=[('sys_token', sys_token.encode('ascii', 'ignore')),
                    ('userid', userid.encode('ascii', 'ignore'))],
            output=[('output', False)])
        monitorExecution(execution, sleepSecs=1)
        token = execution.processOutputs[0].data[0]
    except Exception as e:
        logger.error('generate token failed! userid=%s, error msg=%s' % (userid, e.message))
    return token

def execute_restflow(wps, nodes):
    import json
    nodes_json = json.dumps(nodes)

    # generate url for workflow description
    wf_url = build_request_url(
        wps.url,
        identifier='org.malleefowl.restflow.generate',
        inputs=[('nodes', nodes_json)])
    logger.debug('wf url: %s', wf_url)

    # run workflow
    identifier = 'org.malleefowl.restflow.run'
    inputs = [("workflow_description", wf_url)]
    outputs = [("output",True)]
    execution = wps.execute(identifier, inputs=inputs, output=outputs)

    return execution

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

    def __init__(self, info=False, hide_complex=False, process=None, unknown='ignore', **kw):
        """ Initialise the given mapped schema according to options provided.

        Arguments/Keywords

        info:
           Add info fields for notes and tags (boolean).

           Default: False

        process:
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
        self.hide_complex = hide_complex
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
            elif not self.hide_complex and 'ComplexData' in data_input.dataType:
                node = self.complex_data(data_input)
            elif 'LiteralData' in data_input.dataType:# TODO: workaround for geoserver wps
                node = self.literal_data(data_input)
            else:
                logger.warning('unknown data type %s', data_input.dataType)

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
        if hasattr(data_input, 'defaultValue') and data_input.defaultValue is not None:
            logger.debug("node typ =%s, default value = %s, type=%s",
                         node.typ, data_input.defaultValue, type(data_input.defaultValue))
            if type(node.typ) == colander.DateTime:
                #logger.debug('we have a datetime default value')
                node.default = dateutil.parser.parse(data_input.defaultValue)
            elif type(node.typ) == colander.Boolean:
                # TODO: boolean default does not work ...
                node.default = bool(data_input.defaultValue == 'True')
                logger.debug('boolean default value %s', node.default)
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
        logger.debug('data input type = %s', data_input.dataType)
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
        # TODO: refactor upload, url, text-input choice ...
        ## if metadata is None or metadata == {} or data_input.identifier in metadata.get('uploads', []):
        ##     node = colander.SchemaNode(
        ##         deform.FileData(),
        ##         name=data_input.identifier,
        ##         title=data_input.title,
        ##         widget=deform.widget.FileUploadWidget(tmpstore)
        ##         )
        ## else:
        node = colander.SchemaNode(
            colander.String(),
            name = data_input.identifier,
            title = data_input.title,
            widget = deform.widget.TextInputWidget(),
            validator = colander.url)
           
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
        
    
