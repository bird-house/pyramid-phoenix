import os
import colander
import deform
import dateutil
import re
import types

from pyramid.security import authenticated_userid

from phoenix.widget import BBoxWidget
from phoenix.form import BBoxValidator
from phoenix.form import FileUploadTempStore
from phoenix.form import FileUploadValidator

import logging
logger = logging.getLogger(__name__)


def appstruct_to_inputs(request, appstruct):
    """
    Transforms appstruct to wps inputs.
    """
    logger.debug("appstruct=%s", appstruct)
    inputs = []
    for key,values in appstruct.items():
        if not isinstance(values, types.ListType):
            values = [values]
        for value in values:
            logger.debug("key=%s, value=%s, type=%s", key, value, type(value))
            # check if we have a mapping type for complex input
            if isinstance(value, dict):
                # prefer upload if available
                if value.get('upload', colander.null) is not colander.null:
                    value = value['upload']
                    # logger.debug('uploaded file %s', value)
                    folder = authenticated_userid(request)
                    if not folder:
                        folder = 'guest'
                    logger.debug('folder %s', folder)
                    relpath = os.path.join(folder, value['filename'])
                    # value = 'file://' + request.storage.path(relpath)
                    # value = request.route_url('download', filename=relpath)
                    value = request.storage.url(relpath)
                    # logger.debug('uploaded file as reference = %s', value)
                # otherwise use url
                else:
                    value = value['url']
            inputs.append( (str(key).strip(), str(value).strip()) )
    logger.debug("inputs form appstruct=%s", inputs)
    return inputs

# wps input schema
# ----------------


class WPSSchema(colander.MappingSchema):
    """
    Build a Colander Schema based on the WPS data inputs.

    This Schema generator is based on:
    http://colanderalchemy.readthedocs.io/en/latest/

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
            # elif 'www.w3.org' in data_input.dataType:
            #    node = self.literal_data(data_input)
            elif 'ComplexData' in data_input.dataType:
                if not self.hide_complex:
                    node = self.complex_data(data_input)
            elif 'BoundingBoxData' in data_input.dataType:
                node = self.bbox_data(data_input)
            # elif 'LiteralData' in data_input.dataType:# TODO: workaround for geoserver wps
            #    node = self.literal_data(data_input)
            else:
                # logger.warning('unknown data type %s', data_input.dataType)
                node = self.literal_data(data_input)
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
        node.description = getattr(data_input, 'abstract', '')
        # optional value?
        if data_input.minOccurs == 0:
            node.missing = colander.drop
        # TODO: fix init of default
        if hasattr(data_input, 'defaultValue') and data_input.defaultValue is not None:
            if type(node.typ) == colander.DateTime:
                node.default = dateutil.parser.parse(data_input.defaultValue)
            elif type(node.typ) == colander.Boolean:
                # TODO: boolean default does not work ...
                node.default = bool(data_input.defaultValue == 'True')
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
        # logger.debug('data input type = %s', data_input.dataType)
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
            # logger.debug('allowed values %s', data_input.allowedValues)
            choices = []
            for value in data_input.allowedValues:
                choices.append([value, value])
            node.widget = deform.widget.Select2Widget(values=choices)
        elif type(node.typ) == colander.DateTime:
            node.widget = deform.widget.DateInputWidget()
        elif type(node.typ) == colander.Boolean:
            node.widget = deform.widget.CheckboxWidget()
        elif 'password' in data_input.identifier:
            node.widget = deform.widget.PasswordWidget(size=20)
        else:
            node.widget = deform.widget.TextInputWidget()

    def bbox_data(self, data_input):
        node = colander.SchemaNode(
            colander.String(),
            name=data_input.identifier,
            title=data_input.title,
            validator=BBoxValidator(),
            widget=BBoxWidget()
            )

        # sometimes abstract is not set
        node.description = getattr(data_input, 'abstract', '')
        # optional value?
        if data_input.minOccurs == 0:
            node.missing = colander.drop

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

    def complex_data(self, data_input):
        node = colander.SchemaNode(colander.Mapping(), name=data_input.identifier)
        node.add(self._upload_node(data_input))
        node.add(self._url_node(data_input))

        # sequence of nodes ...
        if data_input.maxOccurs > 1:
            node = colander.SchemaNode(
                colander.Sequence(), 
                node,
                name=data_input.identifier,
                validator=colander.Length(max=data_input.maxOccurs))

        # title
        node.title = data_input.title
        
        # sometimes abstract is not set
        if hasattr(data_input, 'abstract'):
            node.description = data_input.abstract

        # optional value?
        if data_input.minOccurs == 0:
            node.missing = colander.drop
            
        return node

    def _upload_node(self, data_input):
        tmpstore = FileUploadTempStore(self.request)
        node = colander.SchemaNode(
            deform.schema.FileData(),
            name="upload",
            title="Upload",
            description="Either upload a file ...",
            missing = colander.null,
            widget=deform.widget.FileUploadWidget(tmpstore),
            validator=FileUploadValidator(storage=self.request.storage, max_size=self.request.max_file_size))
        return node
    
    def _url_node(self, data_input):
        node = colander.SchemaNode(
            colander.String(),
            name="url",
            title="URL (alternative to upload)",
            description="... or enter a URL pointing to your resource.",
            widget=deform.widget.TextInputWidget(),
            missing=colander.null,
            validator=colander.url)
        
        # check mime-type
        mime_types = []
        if len(data_input.supportedValues) > 0: 
            mime_types = [str(value.mimeType) for value in data_input.supportedValues]
        # logger.debug("mime-types: %s", mime_types)
        # set current proxy certificate
        if 'application/x-pkcs7-mime' in mime_types and self.user is not None:
            # TODO: check if certificate is still valid
            node.default = self.user.get('credentials')

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
        node.description = getattr(data_input, 'abstract', '')

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

