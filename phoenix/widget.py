from colander import (
    Invalid,
    null,
    )

from deform.widget import (
    Widget, 
    TextInputWidget,
    OptGroup, 
    _normalize_choices,
    )

from deform.compat import (
    string_types,
    )

import logging
import json

log = logging.getLogger(__name__)

class TagsWidget(Widget):
    template = 'tags'
    #readonly_template = 'readonly/tags'
    size = None
    strip = True
    mask = None
    mask_placeholder = "_"
    style = None
    requirements = ( ('jquery.maskedinput', None), )

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


class WizardStatesWidget(TextInputWidget):
    """
    Renders a ``<textarea>`` widget.

    **Attributes/Arguments**

    cols
        The size, in columns, of the text input field.  Defaults to
        ``None``, meaning that the ``cols`` is not included in the
        widget output (uses browser default cols).

    rows
        The size, in rows, of the text input field.  Defaults to
        ``None``, meaning that the ``rows`` is not included in the
        widget output (uses browser default cols).

    style
        A string that will be placed literally in a ``style`` attribute on
        the textarea input tag.  For example, 'width:150px;'.  Default:
        ``None``, meaning no style attribute will be added to the input tag.
        
    template
        The template name used to render the widget.  Default:
        ``textarea``.

    readonly_template
        The template name used to render the widget in read-only mode.
        Default: ``readonly/textarea``.


    strip
        If true, during deserialization, strip the value of leading
        and trailing whitespace (default ``True``).
    """
    template = 'wizard_states'
    cols = None
    rows = None
    strip = True
    style = None

class EsgSearchWidget(Widget):
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
        return self.true_val if value == True else self.false_val

    def serialize(self, field, cstruct, readonly=False, **kw):
        log.debug('esgsearch kw: %s', kw)
        search = None
        if cstruct in (null, None):
            search = {}
        else:
            search = json.loads(cstruct)
        kw['url'] = kw.get('url', self.url)
        kw.setdefault('facets', search.get('facets', ''))
        kw.setdefault('query', search.get('query', '*'))
        kw.setdefault('distrib', self._bool( search.get('distrib', True)))
        replica = search.get('replica', False)
        if replica == None:
            kw.setdefault('replica', self.true_val)
        else:
            kw.setdefault('replica', self.false_val)

        latest = search.get('latest', True)
        if latest == True:
            kw.setdefault('latest', self.true_val)
        else:
            kw.setdefault('latest', self.false_val)
        kw.setdefault('temporal', self._bool(search.get('temporal', False)))
        kw.setdefault('spatial', self._bool(search.get('spatial', False)))
        
        kw.setdefault('start', search.get('start', '1600-01-01T12:00:00Z'))
        kw.setdefault('end', search.get('end', '2100-12-31T12:00:00Z'))
        kw.setdefault('bbox', search.get('bbox', '-180,-90,180,90'))
        values = self.get_template_values(field, cstruct, kw)
        log.debug('esgsearch values: %s', values)
        return field.renderer(self.template, **values)

    def deserialize(self, field, pstruct):
        log.debug('esgsearch result pstruct=%s', pstruct)
        if pstruct is null:
            return null

        result = {}
        result['facets'] = pstruct['facets'].strip()
        result['query'] = pstruct['query'].strip()
        result['distrib'] = pstruct.has_key('distrib')
        if pstruct.has_key('replica'):
            result['replica'] = None
        else:
            result['replica'] = False
        if pstruct.has_key('latest'):
            result['latest'] = True
        else:
            result['latest'] = None
        result['start'] = pstruct['start'].strip()
        result['end'] = pstruct['end'].strip()
        result['temporal'] = pstruct.has_key('temporal')
        result['spatial'] = pstruct.has_key('spatial')
        result['bbox'] = pstruct['bbox'].strip()
        try:
            log.debug('hit count: %s', pstruct['hit-count'])
            result['hit-count'] = int(pstruct['hit-count'].strip())
        except:
            result['hit-count'] = 0

        log.debug('esgsearch json result: %s', json.dumps(result))

        if (not result['facets'] and not result['query']):
            return null

        return json.dumps(result)

    def handle_error(self, field, error):
        if field.error is None:
            field.error = error
        for e in error.children:
            for num, subfield in enumerate(field.children):
                if e.pos == num:
                    subfield.widget.handle_error(subfield, e)

class EsgFilesWidget(Widget):
    """
    Widget to select esgf files.
    """
    true_val = 'true'
    false_val = 'false'
    
    template = 'esgfiles'
    values = ()
    search_type = 'File'
    url = ''
    search = {}

    def _bool(self, value):
        return self.true_val if value == True else self.false_val

    def serialize(self, field, cstruct, **kw):
        if cstruct in (null, None):
            cstruct = ()
        values = kw.get('values', self.values)
        kw['values'] = _normalize_choices(values)
        kw['url'] = kw.get('url', self.url)
        search = kw.get('search', self.search)
        log.debug('search: %s', search)
        kw['type'] = kw.get('search_type', self.search_type)
        kw.setdefault('facets', search.get('facets', ''))
        kw.setdefault('query', search.get('query', '*'))
        kw.setdefault('distrib', self._bool( search.get('distrib', True)))
        replica = search.get('replica', False)
        if replica == None:
            kw.setdefault('replica', self.true_val)
        else:
            kw.setdefault('replica', self.false_val)

        latest = search.get('latest', True)
        if latest == True:
            kw.setdefault('latest', self.true_val)
        else:
            kw.setdefault('latest', self.false_val)
        kw.setdefault('temporal', self._bool(search.get('temporal', False)))
        kw.setdefault('spatial', self._bool(search.get('spatial', False)))
        kw.setdefault('start', search.get('start', '2005-01-01T12:00:00Z'))
        kw.setdefault('end', search.get('end', '2005-12-31T12:00:00Z'))
        kw.setdefault('bbox', search.get('bbox', '-180,-90,180,90'))
        tmpl_values = self.get_template_values(field, cstruct, kw)
        return field.renderer(self.template, **tmpl_values)

    def deserialize(self, field, pstruct):
        if pstruct is null:
            return null
        if isinstance(pstruct, string_types):
            return (pstruct,)
        return tuple(pstruct)
    
