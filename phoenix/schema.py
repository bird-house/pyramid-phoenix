import colander
from deform import widget
from .widget import BoundingBoxWidget

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
        if 'boolean' in data_input.dataType:
            cls._add_boolean(schema, data_input)
        elif 'integer' in data_input.dataType:
            cls._add_integer(schema, data_input)
        elif 'float' in data_input.dataType:
            cls._add_float(schema, data_input)
        else:
            cls._add_string(schema, data_input)

    @classmethod
    def _literal_widget(cls, data_input):
        if len(data_input.allowedValues) > 1:
            if not 'AnyValue' in data_input.allowedValues:
                choices = []
                for value in data_input.allowedValues:
                    choices.append([value, value])
                return widget.SelectWidget(values=choices)
        return widget.TextInputWidget()

    @classmethod
    def _add_string(cls, schema, data_input):
        schema.add(colander.SchemaNode(colander.String(), 
                name=data_input.identifier,
                title=data_input.title,
                default=data_input.defaultValue,
                #description=data_input.abstract,
                widget=cls._literal_widget(data_input) ))

    @classmethod
    def _add_integer(cls, schema, data_input):
        schema.add(colander.SchemaNode(colander.Integer(), 
                name=data_input.identifier,
                title=data_input.title,
                default=data_input.defaultValue,
                #description=data_input.abstract,
                widget=cls._literal_widget(data_input) ))
                
    @classmethod
    def _add_float(cls, schema, data_input):
        schema.add(colander.SchemaNode(colander.Float(), 
                name=data_input.identifier,
                title=data_input.title,
                default=data_input.defaultValue,
                #description=data_input.abstract,
                widget=cls._literal_widget(data_input) ))
    @classmethod
    def _add_boolean(cls, schema, data_input):
        schema.add(colander.SchemaNode(colander.Boolean(), 
                name=data_input.identifier,
                title=data_input.title,
                default=data_input.defaultValue,
                #description=data_input.abstract,
                widget=widget.CheckboxWidget()))

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

    
