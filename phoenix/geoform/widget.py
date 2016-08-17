from dateutil import parser as datetime_parser

from colander import (
    Invalid,
    Mapping,
    SchemaNode,
    null,
    )

from deform.compat import (
    text_,
    )

from deform.widget import (
    Widget,
    )

# TODO: replace by real deform
from .deformng import StrippedString

import logging
import json

log = logging.getLogger(__name__)


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
        SchemaNode(StrippedString(), name='minx'),
        SchemaNode(StrippedString(), name='miny'),
        SchemaNode(StrippedString(), name='maxx'),
        SchemaNode(StrippedString(), name='maxy'))

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


class ESGFSearchWidget(Widget):
    """
    Renders an esg search widget

    **Attributes/Arguments**

    template
       The template name used to render the widget.  Default:
        ``esgsearch``.
    """
    true_val = 'true'
    false_val = 'false'

    template = 'esgsearch'
    size = None
    style = None
    requirements = ()
    url = ''

    def _bool(self, value):
        return self.true_val if value is True else self.false_val

    def serialize(self, field, cstruct, readonly=False, **kw):
        log.debug('esgsearch kw: %s', kw)
        search = None
        if cstruct in (null, None):
            search = {}
        else:
            search = json.loads(cstruct)
        kw['url'] = kw.get('url', self.url)
        kw.setdefault('facets', search.get('facets', ''))
        kw.setdefault('query', search.get('query', '*:*'))
        kw.setdefault('distrib', self._bool( search.get('distrib', False)))
        replica = search.get('replica', False)
        if replica is None:
            kw.setdefault('replica', self.true_val)
        else:
            kw.setdefault('replica', self.false_val)

        latest = search.get('latest', True)
        if latest is True:
            kw.setdefault('latest', self.true_val)
        else:
            kw.setdefault('latest', self.false_val)
        kw.setdefault('temporal', self._bool(search.get('temporal', True)))
        # kw.setdefault('spatial', self._bool(search.get('spatial', False)))
        kw.setdefault('spatial', self._bool(False))

        # TODO: quick hack for date format used in esgsearch
        start = search.get('start', '2001-01-01')
        timestamp = datetime_parser.parse(start)
        start = timestamp.isoformat().split('T')[0]
        kw.setdefault('start', start)

        end = search.get('end', '2010-12-31')
        timestamp = datetime_parser.parse(end)
        end = timestamp.isoformat().split('T')[0]
        kw.setdefault('end', end)
        
        # kw.setdefault('bbox', search.get('bbox', '-180,-90,180,90'))
        kw.setdefault('bbox', '-180,-90,180,90')
        values = self.get_template_values(field, cstruct, kw)
        log.debug('esgsearch values: %s', values)
        return field.renderer(self.template, **values)

    def deserialize(self, field, pstruct):
        log.debug('esgsearch result pstruct=%s', pstruct)
        if pstruct is null:
            return null

        result = dict(
            facets=pstruct['facets'].strip(),
            query=pstruct['query'].strip(),
            distrib=pstruct.has_key('distrib'))
        if 'replica' in pstruct:
            result['replica'] = None
        else:
            result['replica'] = False
        if pstruct.has_key('latest'):
            result['latest'] = True
        else:
            result['latest'] = None
        # TODO: quick hack for date format used in esgsearch
        result['start'] = pstruct['start'].strip() + "T12:00:00Z"
        result['end'] = pstruct['end'].strip() + "T12:00:00Z"
        result['temporal'] = pstruct.has_key('temporal')
        # result['spatial'] = pstruct.has_key('spatial')
        result['spatial'] = False
        # result['bbox'] = pstruct['bbox'].strip()
        result['bbox'] = '-180,-90,180,90'
        try:
            log.debug('hit count: %s', pstruct['hit-count'])
            result['hit-count'] = int(pstruct['hit-count'].strip())
        except:
            result['hit-count'] = 0

        log.debug('esgsearch json result: %s', json.dumps(result))

        if not result['facets'] and not result['query']:
            return null

        return json.dumps(result)

    def handle_error(self, field, error):
        if field.error is None:
            field.error = error
        for e in error.children:
            for num, subfield in enumerate(field.children):
                if e.pos == num:
                    subfield.widget.handle_error(subfield, e)

