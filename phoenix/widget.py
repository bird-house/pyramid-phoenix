import deform
import colander

class BoundingBoxWidget(deform.widget.Widget):

    template = 'boundingbox'
    size = None
    strip = True
    mask = None
    mask_placeholder = "_"
    style = None
    requirements = (('jquery.maskedinput', None),)

    def __init__(self, *args, **kwargs):
        deform.widget.Widget.__init__(self, *args, **kwargs)

    def serialize(self, field, cstruct, **kw):
        if cstruct in (colander.null, None):
            LowerCorner1 = ''
            LowerCorner2 = ''
            UpperCorner1 = ''
            UpperCorner2 = ''
        else:
            LowerCorner1, LowerCorner2,\
            UpperCorner1, UpperCorner2 = cstruct.split(' ', 3)

        kw.setdefault('LowerCorner1', LowerCorner1)
        kw.setdefault('LowerCorner2', LowerCorner2)
        kw.setdefault('UpperCorner1', UpperCorner1)
        kw.setdefault('UpperCorner2', UpperCorner2)

        values = self.get_template_values(field, cstruct, kw)

        return field.renderer('boundingbox', **values)

    def deserialize(self, field, pstruct):
        if pstruct in ('', colander.null):
            return colander.null

        return ' '.join([pstruct['LowerCorner1'], pstruct['LowerCorner2'],
                         pstruct['UpperCorner2'], pstruct['UpperCorner2']])



