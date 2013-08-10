from colander import (
    Invalid,
    null,
    )

from deform.widget import Widget
#import cgi

from pyesgf.search import SearchConnection

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
        if pstruct is null:
            return null
        if self.strip:
            pstruct = pstruct.strip()
        if not pstruct:
            return null
        return pstruct

    def handle_error(self, field, error):
        if field.error is None:
            field.error = error
        for e in error.children:
            for num, subfield in enumerate(field.children):
                if e.pos == num:
                    subfield.widget.handle_error(subfield, e)
