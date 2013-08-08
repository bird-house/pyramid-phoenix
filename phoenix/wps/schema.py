# wpsschema.py
# Copyright (C) 2013 the ClimDaPs/Phoenix authors and contributors
# <see AUTHORS file>
#
# This module is part of ClimDaPs/Phoenix and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import colander
import deform
import logging

import dateutil
import re

__all__ = ['WPSInputSchemaNode', 'output_schema']

log = logging.getLogger(__name__)

# Memory tempstore for file uploads
# ---------------------------------

class MemoryTmpStore(dict):
    """ Instances of this class implement the
    :class:`deform.interfaces.FileUploadTempStore` interface"""
    def preview_url(self, uid):
        return None

tmpstore = MemoryTmpStore()


# input data
# ----------


class WPSInputSchemaNode(colander.SchemaNode):
    """ Build a Colander Schema based on the WPS data inputs.

    This Schema generator is based on:
    http://colanderalchemy.readthedocs.org/en/latest/

    TODO: use widget category as grouping info
    TODO: fix dataType in wps client
    """

    appstruct = {}

    def __init__(self, process=None, unknown='ignore', **kw):
        """ Initialise the given mapped schema according to options provided.

        Arguments/Keywords

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

        log.debug('DataInputsSchemaNode.__init__: process=%s, kw=%s', process, kw)

        kwargs = kw.copy()

        # The default type of this SchemaNode is Mapping.
        colander.SchemaNode.__init__(self, colander.Mapping(unknown), **kwargs)
        self.process = process
        self.unknown = unknown
        self.kwargs = kwargs or {}   

        self.add_nodes(process)    
        
    def add_nodes(self, process):
        if process is None:
            return

        log.debug("adding nodes for process inputs, num inputs = %s", len(process.dataInputs))

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
                log.debug('we have a datetime default value')
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

    def colander_literal_widget(self, node, data_input):
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
        elif 'password' in data_input.identifier:
            node.widget = deform.widget.PasswordWidget(size=20)
        else:
            node.widget = deform.widget.TextInputWidget()

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
        cloned = self.__class__(self.process,
                                self.unknown,
                                **self.kwargs)
        cloned = self.clone()
        cloned._bind(kw)

        log.debug('after bind: num schema children = %s', len(cloned.children))
        return cloned

    def clone(self):
        cloned = self.__class__(self.process,
                                self.unknown,
                                **self.kwargs)
        cloned.__dict__.update(self.__dict__)
        cloned.children = [node.clone() for node in self.children]
        return cloned
        
    
