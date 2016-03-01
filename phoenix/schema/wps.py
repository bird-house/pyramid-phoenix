import colander
import deform
import dateutil
import re

from phoenix.views.form import FileUploadTempStore, MemoryTempStore

import logging
logger = logging.getLogger(__name__)


# wps input schema
# ----------------

class WPSSchema(colander.MappingSchema):
    """
    Build a Colander Schema based on the WPS data inputs.

    This Schema generator is based on:
    http://colanderalchemy.readthedocs.org/en/latest/

    TODO: fix dataType in wps client
    """

    appstruct = {}

    def __init__(self, request, hide_complex=False, process=None, unknown='ignore', user=None, **kw):
        """ Initialise the given mapped schema according to options provided.

        Arguments/Keywords

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
        self.request = request
        self.hide_complex = hide_complex
        self.process = process
        self.unknown = unknown
        self.user = user
        self.kwargs = kwargs or {}
        self.add_nodes(process)
        
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
        # TODO: refactor upload
        node = None
        if True:
            tmpstore = MemoryTempStore(self.request)
            node = colander.SchemaNode(
                deform.FileData(),
                name=data_input.identifier,
                title=data_input.title,
                widget=deform.widget.FileUploadWidget(tmpstore))
        else:
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

        # check mime-type
        mime_types = []
        if len(data_input.supportedValues) > 0: 
            mime_types = [str(value.mimeType) for value in data_input.supportedValues]
        logger.debug("mime-types: %s", mime_types)
        # set current proxy certificate
        if 'application/x-pkcs7-mime' in mime_types and self.user is not None:
            # TODO: check if certificate is still valid
            node.default = self.user.get('credentials')

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
            self.request,
            self.hide_complex,
            self.process,
            self.unknown,
            self.user,
            **self.kwargs)
        cloned.__dict__.update(self.__dict__)
        cloned.children = [node.clone() for node in self.children]
        return cloned
        
    
