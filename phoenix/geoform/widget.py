from dateutil import parser as datetime_parser
from datetime import datetime
from os import path

from colander import (
    Invalid,
    Mapping,
    SchemaNode,
    null,
)

from deform.compat import (
    string_types,
    text_,
)

from deform.widget import (
    Widget,
)

from deform.widget import (
    FileUploadWidget as FUW
)

from deform.widget import _StrippedString

import logging
import json

LOGGER = logging.getLogger("PHOENIX")


class ResourceWidget(Widget):
    """
    Renders an WPS ComplexType input widget with an upload button.

    It is based on deform.widget.TextInputWidget.
    """
    template = 'resource'
    readonly_template = 'readonly/textinput'
    strip = True
    mask = None
    mask_placeholder = "_"
    mime_types = ['application/x-netcdf']
    upload = False
    storage_url = None
    size_limit = 2 * 1024 * 1024  # 2 MB in bytes
    requirements = (('jquery.maskedinput', None),)

    def serialize(self, field, cstruct, **kw):
        if cstruct in (null, None):
            cstruct = ''
        readonly = kw.get('readonly', self.readonly)
        template = readonly and self.readonly_template or self.template
        values = self.get_template_values(field, cstruct, kw)
        return field.renderer(template, **values)

    def deserialize(self, field, pstruct):
        if pstruct is null:
            return null
        elif not isinstance(pstruct, string_types):
            raise Invalid(field.schema, "Pstruct is not a string")
        if self.strip:
            pstruct = pstruct.strip()
        if not pstruct:
            return null
        LOGGER.debug("pstruct: %s", pstruct)
        return pstruct


class DateSliderWidget(Widget):
    """
    Renders a date range slider widget.

    The range for the widget is taken from the default values.
    If no defaults are set the the range is set to 1900/01/01 to 2100/12/31.
    """
    template = 'range_slider_date'
    readonly_template = 'readonly/textinput'

    def serialize(self, field, cstruct, **kw):
        # set default values
        min_value = datetime.strptime('1900-01-01', '%Y-%m-%d').timestamp() * 1000
        max_value = datetime.strptime('2100-12-31', '%Y-%m-%d').timestamp() * 1000

        if cstruct in (null, None):
            cstruct = ''

        # check if the wps defaults can be used to
        # set the default values of the range
        elif len(cstruct.split('/')) == 2:
            min_value, max_value = cstruct.split('/', 1)
            if len(min_value.split("-")) == 3 and len(max_value.split("-")) == 3:
                # its a date
                min_value = datetime.strptime(min_value, '%Y-%m-%d').timestamp() * 1000
                max_value = datetime.strptime(max_value, '%Y-%m-%d').timestamp() * 1000

        kw.setdefault('min_default', min_value)
        kw.setdefault('max_default', max_value)
        kw.setdefault('min', min_value)
        kw.setdefault('max', max_value)

        readonly = kw.get('readonly', self.readonly)
        template = readonly and self.readonly_template or self.template
        values = self.get_template_values(field, cstruct, kw)
        return field.renderer(template, **values)

    def deserialize(self, field, pstruct):
        if pstruct is null:
            return null
        elif not isinstance(pstruct, string_types):
            raise Invalid(field.schema, "Pstruct is not a string")
        if not pstruct:
            return null
        min_date, max_date = pstruct.split("|")
        min_date = datetime.fromtimestamp(float(min_date) / 1000).strftime('%Y-%m-%d')
        max_date = datetime.fromtimestamp(float(max_date) / 1000).strftime('%Y-%m-%d')
        pstruct = "{}/{}".format(min_date, max_date)
        LOGGER.debug("pstruct: %s", pstruct)
        return pstruct


class RangeSliderWidget(Widget):
    """
    Renders a range slider widget.

    The range for the widget is taken from the default values.
    If no defaults are set the the range is set to 1 to 100.
    """
    template = 'range_slider'
    readonly_template = 'readonly/textinput'

    def serialize(self, field, cstruct, **kw):
        # set default values
        min_value = '1'
        max_value = '100'

        if cstruct in (null, None):
            cstruct = ''

        # check if the wps defaults can be used to
        # set the default values of the range
        elif len(cstruct.split('/')) == 2:
            min_value, max_value = cstruct.split('/', 1)
            try:
                int(min_value)
                int(max_value)
            except ValueError:
                min_value = '1'
                max_value = '100'

        kw.setdefault('min_default', min_value)
        kw.setdefault('max_default', max_value)
        kw.setdefault('min', min_value)
        kw.setdefault('max', max_value)

        readonly = kw.get('readonly', self.readonly)
        template = readonly and self.readonly_template or self.template
        values = self.get_template_values(field, cstruct, kw)
        return field.renderer(template, **values)

    def deserialize(self, field, pstruct):
        if pstruct is null:
            return null
        elif not isinstance(pstruct, string_types):
            raise Invalid(field.schema, "Pstruct is not a string")
        if not pstruct:
            return null
        pstruct = pstruct.replace("|", "/")
        LOGGER.debug("pstruct: %s", pstruct)
        return pstruct


class FileUploadWidget(FUW):
    """
    This is a customisation of the deform FileUploadWidget.

    A file will be uploaded and stored to disk, the result from the "deserialize" will
    be a string containing the path of the file.
    As a result the "serialize" has to take that string and get the filedict object.
    """
    def __init__(self, tmpstore, wps_id, process_id):
        super().__init__(tmpstore)
        self.wps_id = wps_id
        self.process_id = process_id

    def random_id(self):
        uid = super().random_id()
        today = datetime.today().strftime("%Y-%m-%d")
        return path.join(today, self.wps_id, self.process_id, uid)

    def serialize(self, field, cstruct, **kw):
        if cstruct in (null, None):
            cstruct = {}
        if cstruct:
            # all we have is a string containing the uid, we need to get a
            # FileUploadTempStore object
            uid = cstruct
            cstruct = self.tmpstore[uid]
            if cstruct is None:
                cstruct = {}

        readonly = kw.get("readonly", self.readonly)
        template = readonly and self.readonly_template or self.template
        values = self.get_template_values(field, cstruct, kw)
        return field.renderer(template, **values)

    def deserialize(self, field, pstruct):
        # We do not want to pass the data to the WPS, only the location of the data,
        # which we have stored in a directory identified by the uid
        data = super().deserialize(field, pstruct)
        if data is null:
            return data

        return path.join(self.tmpstore.storage_url, data["uid"], data["filename"])


class BBoxWidget(Widget):
    """
    Renders a BoundingBox Widget.

    **Attributes/Arguments**
    template
        The template name used to render the input widget.  Default:
        ``bbox``.
    readonly_template
        The template name used to render the widget in read-only mode.
        Default: ``readonly/bbox``.
    """
    template = 'bbox'
    readonly_template = 'readonly/bbox'

    _pstruct_schema = SchemaNode(
        Mapping(),
        SchemaNode(_StrippedString(), name='minx'),
        SchemaNode(_StrippedString(), name='miny'),
        SchemaNode(_StrippedString(), name='maxx'),
        SchemaNode(_StrippedString(), name='maxy'))

    def serialize(self, field, cstruct, **kw):
        if cstruct is null:
            minx = '-180'
            miny = '-90'
            maxx = '180'
            maxy = '90'
        else:
            minx, miny, maxx, maxy = cstruct.split(',', 3)

        kw.setdefault('minx', minx)
        kw.setdefault('miny', miny)
        kw.setdefault('maxx', maxx)
        kw.setdefault('maxy', maxy)

        # readonly = kw.get('readonly', self.readonly)
        # TODO: add readonly template
        readonly = False
        template = readonly and self.readonly_template or self.template
        values = self.get_template_values(field, cstruct, kw)
        return field.renderer(template, **values)

    def deserialize(self, field, pstruct):
        if pstruct is null:
            return null
        else:
            try:
                validated = self._pstruct_schema.deserialize(pstruct)
            except Invalid as exc:
                raise Invalid(field.schema, text_("Invalid pstruct: %s" % exc))
            minx = validated['minx']
            miny = validated['miny']
            maxx = validated['maxx']
            maxy = validated['maxy']

            if not minx and not minx and not maxx and not maxy:
                return null

            result = ','.join([minx, miny, maxx, maxy])

            if not minx or not miny or not maxx or not maxy:
                raise Invalid(field.schema, 'Incomplete bbox', result)

            return result


class TagsWidget(Widget):
    template = 'tags'
    # readonly_template = 'readonly/tags'
    size = None
    strip = True
    mask = None
    mask_placeholder = "_"
    style = None
    requirements = (('jquery.maskedinput', None), )

    def serialize(self, field, cstruct, **kw):
        if cstruct in (null, None):
            cstruct = ''
        values = self.get_template_values(field, cstruct, kw)
        return field.renderer(self.template, **values)

    def deserialize(self, field, pstruct):
        LOGGER.debug('result pstruct=%s', pstruct)
        if pstruct is null:
            return null
        if self.strip:
            pstruct = pstruct.strip()
        if not pstruct:
            return null
        return pstruct
