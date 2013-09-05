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

import logging

log = logging.getLogger(__name__)

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

    template = 'esgsearch'
    size = None
    strip = True
    query = '*'
    mask = None
    mask_placeholder = "_"
    style = None
    requirements = ( ('jquery.maskedinput', None), )

    def serialize(self, field, cstruct, readonly=False, **kw):
        if cstruct in (null, None):
            cstruct = ''
        kw.setdefault('query', self.query)
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
        #query = pstruct.get('%s-query' % (field.name,)) or '*'
        #setattr(field, '%s-query' % (field.name,), query)
        return pstruct

    def handle_error(self, field, error):
        if field.error is None:
            field.error = error
        for e in error.children:
            for num, subfield in enumerate(field.children):
                if e.pos == num:
                    subfield.widget.handle_error(subfield, e)

class EsgFilesWidget(Widget):
    """
    Renders an esg files widget

    **Attributes/Arguments**

    template
       The template name used to render the widget.  Default:
        ``esgfiles``.
    """

    template = 'esgfiles'
    null_value = ''
    values = ()
    size = None
    multiple = False
    optgroup_class = OptGroup
    long_label_generator = None

    def serialize(self, field, cstruct, **kw):
        if cstruct in (null, None):
            cstruct = self.null_value
        readonly = kw.get('readonly', self.readonly)
        values = kw.get('values', self.values)
        template = readonly and self.readonly_template or self.template
        kw['values'] = _normalize_choices(values)
        tmpl_values = self.get_template_values(field, cstruct, kw)
        return field.renderer(template, **tmpl_values)

    def deserialize(self, field, pstruct):
        if pstruct in (null, self.null_value):
            return null
        return pstruct

