import dateutil

import colander
from deform import widget
from .widget import BoundingBoxWidget

import logging

log = logging.getLogger(__name__)

# Ouput Details ...
# -----------------

class OutputContent(colander.MappingSchema):
    data = colander.SchemaNode(
        colander.String(),
        widget=widget.TextInputWidget())
    reference = colander.SchemaNode(
        colander.Boolean(),
        widget=widget.CheckboxWidget())

class OutputContents(colander.SequenceSchema):
    content = OutputContent()

class OutputDetails(colander.MappingSchema):
    identifier = colander.SchemaNode(
        colander.String(),
        widget=widget.TextInputWidget())
    complete = colander.SchemaNode(
        colander.Boolean(),
        widget=widget.CheckboxWidget())
    succeded = colander.SchemaNode(
        colander.Boolean(),
        widget=widget.CheckboxWidget())

    contents = OutputContents()


# DataInputs ...
# ---------------

 
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
            cls._colander_type(data_input),
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
        cls._colander_widget(node, data_input)

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
    def _colander_type(cls, data_input):
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
    def _colander_widget(cls, node, data_input):
        if len(data_input.allowedValues) > 1:
            if not 'AnyValue' in data_input.allowedValues:
                choices = []
                for value in data_input.allowedValues:
                    choices.append([value, value])
                node.widget = widget.SelectWidget(values=choices)
        elif type(node.typ) == colander.DateTime:
            node.widget = widget.DateInputWidget()
        else:
            node.widget = widget.TextInputWidget()

    @classmethod
    def _add_complex_data(cls, schema, data_input):
        schema.add(colander.SchemaNode(
              colander.String(),
              name=data_input.identifier,
              title=data_input.title,
              #description=data_input.abstract,
              widget=widget.TextAreaWidget(rows=5),
              ))

    @classmethod
    def _add_boundingbox(cls, schema, data_input):
        schema.add(colander.SchemaNode(
            colander.String(),
            name=data_input.identifier,
            title=data_input.title,
            #description=data_input.abstract,
            widget=BoundingBoxWidget(),
            ))

    
