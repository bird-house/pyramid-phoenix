from dateutil import parser as datetime_parser

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

from deform.widget import _StrippedString

import logging
import json

log = logging.getLogger(__name__)


class ResourceWidget(Widget):
    """
    Renders an WPS ComplexType input widget with a cart and upload button.

    It is based on deform.widget.TextInputWidget.
    """
    template = 'resource'
    readonly_template = 'readonly/textinput'
    strip = True
    mask = None
    mask_placeholder = "_"
    cart = False
    mime_types = ['application/x-netcdf']
    upload = False
    storage_url = None
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
        log.debug("pstruct: %s", pstruct)
        return pstruct


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
        log.debug('result pstruct=%s', pstruct)
        if pstruct is null:
            return null
        if self.strip:
            pstruct = pstruct.strip()
        if not pstruct:
            return null
        return pstruct
