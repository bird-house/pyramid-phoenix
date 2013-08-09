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

    conn = SearchConnection("http://esgf-data.dkrz.de/esg-search", distrib=False)
    ctx = conn.new_context(project='CMIP5', product='output1', replica=False, latest=True)
    constraints = {'institute': 'MPI-M'}
    facet = 'institute'

    def serialize(self, field, cstruct, **kw):
        if cstruct in (null, None):
            cstruct = ''
        constraints = kw.get('constraints', self.constraints)
        kw['constraints'] = constraints
        ctx = kw.get('ctx', self.ctx)
        kw['ctx'] = ctx
        kw['facet'] = self.facet
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