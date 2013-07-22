# Author:   Carsten Ehbrecht
#           ehbrecht@dkrz.de
#
# TODO: schema code quite dirty. Needs refactoring!



import dateutil
import re

import colander
import deform

import logging

log = logging.getLogger(__name__)

# Memory tempstore for file uploads
# ---------------------------------

class MemoryTmpStore(dict):
    """ Instances of this class implement the
    :class:`deform.interfaces.FileUploadTempStore` interface"""
    def preview_url(self, uid):
        return None

tmpstore = MemoryTmpStore()

class AdminSchema(colander.MappingSchema):
    history_count = colander.SchemaNode(
        colander.Int(),
        name = 'history_count',
        title = "Number of Processings",
        missing = 0,
        widget = deform.widget.TextInputWidget(readonly=True)
        )

@colander.deferred
def deferred_category_widget(node, kw):
    ctx = kw.get('search_context')
    keys = ctx.facet_counts.keys()
    choices = zip(keys, keys)
    return deform.widget.SelectWidget(values = choices)

@colander.deferred
def deferred_facet_widget(node, kw):
    ctx = kw.get('search_context')
    category = kw.get('category')
    keys = ctx.facet_counts[category].keys()
    choices = zip(keys, keys)
    return deform.widget.SelectWidget(values = choices)

@colander.deferred
def deferred_tags_widget(node, kw):
    ctx = kw.get('search_context')
    tags = kw.get('tags')
    if tags and len(tags) > 0:
        choices = zip(tags, tags)
    else:
        choices = []
    #return deform_bootstrap_extra.widgets.TagsWidget()
    return deform.widget.SelectWidget(values = choices)

class SearchSchema(colander.MappingSchema):
    category = colander.SchemaNode(
        colander.String(),
        name = 'category',
        title = 'Category',
        description = 'Choose search category',
        widget = deferred_category_widget)

    facet = colander.SchemaNode(
        colander.String(),
        description = 'Choose facet',
        widget = deferred_facet_widget)

    tags = colander.SchemaNode(
        colander.String(),
        description = 'Choosen tags',
        missing = '',
        widget = deferred_tags_widget)

@colander.deferred
def deferred_wps_list_widget(node, kw):
    wps_list = kw.get('wps_list', [])
    readonly = kw.get('readonly', False)
    return deform.widget.RadioChoiceWidget(
        values=wps_list,
        readonly=readonly)

class CatalogAddWPSSchema(colander.MappingSchema):
    current_wps = colander.SchemaNode(
        colander.String(),
        title = "WPS List",
        description = 'List of known WPS',
        missing = '',
        widget=deferred_wps_list_widget)

    wps_url = colander.SchemaNode(
        colander.String(),
        title = 'WPS URL',
        description = 'Add new WPS URL',
        missing = '',
        default = '',
        validator = colander.url,
        widget = deform.widget.TextInputWidget())

class CatalogSelectWPSSchema(colander.MappingSchema):
   
    active_wps = colander.SchemaNode(
        colander.String(),
        title = 'WPS',
        description = "Select active WPS",
        widget = deferred_wps_list_widget
        )

# DataInputs ...
# ---------------

# TODO: use widget category as grouping info
 
# schema is build dynamically
class DataInputsSchema(colander.MappingSchema):
    @classmethod
    def build(cls, schema, process):
        # TODO: what is the right way to build schema dynamically?
        # TODO: fix dataType in wps client
        for data_input in process.dataInputs:
            if data_input.dataType == None:
                cls._add_boundingbox(schema, data_input) 
            elif 'www.w3.org' in data_input.dataType:
                cls._add_literal_data(schema, data_input)
            elif 'ComplexData' in data_input.dataType:
                cls._add_complex_data(schema, data_input)
            else:
                raise Exception('unknown data type %s' % (data_input.dataType))
                         

    @classmethod
    def _add_literal_data(cls, schema, data_input):
        node = colander.SchemaNode(
            cls._colander_literal_type(data_input),
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
                log.debug('we have a datetime default value')
                node.default = dateutil.parser.parse(data_input.defaultValue)
            else:
                node.default = data_input.defaultValue
        cls._colander_literal_widget(node, data_input)

        # sequence of nodes ...
        if data_input.maxOccurs > 1:
            schema.add(colander.SchemaNode(
                colander.Sequence(), 
                node,
                name=data_input.identifier,
                title=data_input.title,
                validator=colander.Length(max=data_input.maxOccurs)
                ))
        else:
            schema.add(node)

    @classmethod
    def _colander_literal_type(cls, data_input):
        log.debug('data input type = %s', data_input.dataType)
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

    @classmethod
    def _colander_literal_widget(cls, node, data_input):
        if len(data_input.allowedValues) > 1:
            if not 'AnyValue' in data_input.allowedValues:
                choices = []
                for value in data_input.allowedValues:
                    choices.append([value, value])
                node.widget = deform.widget.SelectWidget(values=choices)
        elif type(node.typ) == colander.DateTime:
            node.widget = deform.widget.DateInputWidget()
        elif type(node.typ) == colander.Boolean:
            node.widget = deform.widget.CheckboxWidget()
        else:
            node.widget = deform.widget.TextInputWidget()

    @classmethod
    def _add_complex_data(cls, schema, data_input):
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
            schema.add(colander.SchemaNode(
                colander.Sequence(), 
                node,
                name=data_input.identifier,
                title=data_input.title,
                validator=colander.Length(max=data_input.maxOccurs)
                ))
        else:
            schema.add(node)

    @classmethod
    def _add_boundingbox(cls, schema, data_input):
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
            schema.add(colander.SchemaNode(
                colander.Sequence(), 
                node,
                name=data_input.identifier,
                title=data_input.title,
                validator=colander.Length(max=data_input.maxOccurs)
                ))
        else:
            schema.add(node)
        
    
# Ouput Data ...
# -----------------

def output_schema():
    # data
    data = colander.SchemaNode(colander.Mapping())
    data.add(colander.SchemaNode(colander.String(), name='value',
        missing = colander.drop))
    data.add(colander.SchemaNode(colander.String(), name='reference',
        missing = colander.drop))
    data.add(colander.SchemaNode(colander.String(), name='mime_type',
        missing = colander.drop))

    # output
    output = colander.SchemaNode(colander.Mapping())
    output.add(colander.SchemaNode(colander.String(), name = 'name'))
    output.add(colander.SchemaNode(colander.String(), name = 'reference',
        missing = colander.drop))
    output.add(colander.SchemaNode(colander.String(), name = 'mime_type'))
    output.add(colander.SchemaNode(colander.String(), name = 'data_type'))
    # data sequence
    output.add(colander.SchemaNode(colander.Sequence(), data, name = 'data'))
        
    # process output
    schema = colander.SchemaNode(colander.Mapping())
    schema.add(colander.SchemaNode(colander.String(), name = 'identifier'))
    schema.add(colander.SchemaNode(colander.Boolean(), name = 'complete'))
    schema.add(colander.SchemaNode(colander.Boolean(), name = 'succeded'))

    # output sequence
    schema.add(colander.SchemaNode(colander.Sequence(), output, name="outputs"))

    return schema
      

    
