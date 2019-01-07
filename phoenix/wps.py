import os
import colander
import deform
import dateutil
import re
import types
import uuid
import requests
from lxml import etree

from owslib.wps import WPSExecution

from pyramid.security import authenticated_userid

from phoenix._compat import PY2, text_type
from phoenix.geoform.widget import BBoxWidget, ResourceWidget
from phoenix.geoform.form import BBoxValidator
from phoenix.geoform.form import URLValidator
from phoenix.geoform.form import TextValidator

import logging
LOGGER = logging.getLogger("PHOENIX")


OPENDAP_MIME_TYPES = ['application/x-ogc-dods']


def is_opendap(data_input):
    if hasattr(data_input, 'metadata'):
        for metadata in data_input.metadata:
            if metadata.title in OPENDAP_MIME_TYPES:
                return True
    return False


def check_status(url=None, response=None, sleep_secs=2, verify=False):
    """
    Run owslib.wps check_status with additional exception handling.

    :param verify: Flag to enable SSL verification. Default: False
    :return: OWSLib.wps.WPSExecution object.
    """
    execution = WPSExecution()
    if response:
        LOGGER.debug("using response document ...")
        xml = response
    elif url:
        LOGGER.debug('using status_location url ...')
        xml = requests.get(url, verify=verify).content
    else:
        raise Exception("you need to provide a status-location url or response object.")
    # TODO: see owslib: https://github.com/geopython/OWSLib/pull/477
    if PY2 and isinstance(xml, text_type):
        xml = xml.encode('utf8', errors='ignore')
    execution.checkStatus(response=xml, sleepSecs=sleep_secs)
    if execution.response is None:
        raise Exception("check_status failed!")
    # TODO: workaround for owslib type change of reponse
    if not isinstance(execution.response, etree._Element):
        execution.response = etree.fromstring(execution.response)
    return execution


def appstruct_to_inputs(request, appstruct):
    """
    Transforms appstruct to wps inputs.
    """
    # LOGGER.debug("appstruct=%s", appstruct)
    inputs = []
    for key, values in appstruct.items():
        if key in ['_async_check', 'csrf_token']:
            continue
        if not isinstance(values, types.ListType):
            values = [values]
        for value in values:
            # LOGGER.debug("key=%s, value=%s, type=%s", key, value, type(value))
            inputs.append((str(key).strip(), str(value).strip()))
    # LOGGER.debug("inputs form appstruct=%s", inputs)
    return inputs

# wps input schema
# ----------------


class WPSSchema(deform.schema.CSRFSchema):
    """
    Build a Colander Schema based on the WPS data inputs.

    This Schema generator is based on:
    http://colanderalchemy.readthedocs.io/en/latest/

    TODO: fix dataType in wps client
    """

    appstruct = {}

    def __init__(self, request, hide_complex=False, process=None, use_async=False, user=None, **kw):
        """ Initialise the given mapped schema according to options provided.

        Arguments/Keywords

        process:
           An ``WPS`` process description that you want a ``Colander`` schema
           to be generated for.

        \*\*kw
           Represents *all* other options able to be passed to a
           :class:`colander.SchemaNode`. Keywords passed will influence the
           resulting mapped schema accordingly (for instance, passing
           ``title='My Model'`` means the returned schema will have its
           ``title`` attribute set accordingly.

           See http://docs.pylonsproject.org/projects/colander/en/latest/basics.html for more information.
        """

        kwargs = kw.copy()

        super(WPSSchema, self).__init__(**kwargs)
        self.request = request
        self.hide_complex = hide_complex
        self.process = process
        self.user = user
        self.kwargs = kwargs or {}
        if use_async:
            self.add_async_check()
        self.add_nodes(process)

    def add_async_check(self):
        node = colander.SchemaNode(
            colander.Boolean(),
            name='_async_check',
            title='Run async',
            description='Check this to run process async.',
            default=True,
            widget=deform.widget.CheckboxWidget(),
        )
        self.add(node)

    def add_nodes(self, process):
        if process is None:
            return
        for data_input in process.dataInputs:
            if 'ComplexData' in data_input.dataType:
                if not self.hide_complex:
                    self.add(self.complex_data(data_input))
            elif 'BoundingBoxData' in data_input.dataType:
                self.add(self.bbox_data(data_input))
            else:
                self.add(self.literal_data(data_input))

    def literal_data(self, data_input):
        node = colander.SchemaNode(
            self.colander_literal_type(data_input),
            name=data_input.identifier,
            title=data_input.title,
            validator=TextValidator(),
        )

        # sometimes abstract is not set
        node.description = getattr(data_input, 'abstract', '')
        # optional value?
        if data_input.minOccurs == 0:
            node.missing = colander.drop
        # TODO: fix init of default
        if hasattr(data_input, 'defaultValue') \
           and data_input.defaultValue is not None:
            if type(node.typ) in (colander.DateTime, colander.Date,
                                  colander.Time):
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
        # LOGGER.debug('data input type = %s', data_input.dataType)
        if 'boolean' in data_input.dataType:
            return colander.Boolean()
        elif 'integer' in data_input.dataType:
            return colander.Integer()
        elif 'float' in data_input.dataType:
            return colander.Float()
        elif 'double' in data_input.dataType:
            return colander.Float()
        elif 'angle' in data_input.dataType:
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
                dateutil.parser.parse(data_input.defaultValue)
            except Exception:
                return colander.String()
            else:
                return colander.DateTime()
        else:
            return colander.String()

    def colander_literal_widget(self, node, data_input):
        if len(data_input.allowedValues) > 0 and 'AnyValue' not in data_input.allowedValues:
            # LOGGER.debug('allowed values %s', data_input.allowedValues)
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
        elif type(node.typ) == colander.String:
            if is_opendap(data_input):
                node.widget = ResourceWidget(
                    cart=self.request.has_permission('edit'),
                    mime_types=OPENDAP_MIME_TYPES,
                    upload=False,
                    storage_url=self.request.storage.base_url)
            else:
                node.widget = deform.widget.TextInputWidget()
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
        node.description = getattr(data_input, 'abstract') or 'No summary'
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
        mime_types = [value.mimeType for value in data_input.supportedValues]
        LOGGER.debug("mime_types for resource widget: %s", mime_types)
        widget = ResourceWidget(
            cart=self.request.has_permission('edit'),
            mime_types=mime_types,
            upload=True,
            storage_url=self.request.storage.base_url,
            size_limit=self.request.max_file_size * 1048576)

        resource_node = colander.SchemaNode(
            colander.String(),
            name=data_input.identifier,
            title="Resource",
            description="Enter a URL pointing to your resource.",
            widget=widget,
            default=self._url_node_default(data_input),
            validator=URLValidator(),
        )

        # sequence of nodes ...
        if data_input.maxOccurs > 1:
            node = colander.SchemaNode(
                colander.Sequence(),
                resource_node,
                name=data_input.identifier,
                validator=colander.Length(max=data_input.maxOccurs))
        else:
            node = resource_node

        # title
        node.title = data_input.title or data_input.identifier

        # sometimes abstract is not set
        node.description = getattr(data_input, 'abstract') or 'No summary'

        # optional value?
        if data_input.minOccurs == 0:
            node.missing = colander.drop

        return node

    def _url_node_default(self, data_input):
        # check mime-type
        mime_types = []
        if len(data_input.supportedValues) > 0:
            mime_types = [str(value.mimeType) for value in data_input.supportedValues]
        # LOGGER.debug("mime-types: %s", mime_types)
        # set current proxy certificate
        if 'application/x-pkcs7-mime' in mime_types and self.user is not None:
            # TODO: check if certificate is still valid
            default = self.user.get('credentials')
        else:
            default = colander.null
        return default

    def bind(self, **kw):
        cloned = self.clone()
        cloned._bind(kw)

        LOGGER.debug('after bind: num schema children = %s', len(cloned.children))
        return cloned

    def clone(self):
        cloned = self.__class__(
            self.request,
            self.hide_complex,
            self.process,
            self.user,
            **self.kwargs)
        cloned.__dict__.update(self.__dict__)
        cloned.children = [node.clone() for node in self.children]
        return cloned
