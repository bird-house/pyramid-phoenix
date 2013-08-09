from colander import (
    Invalid,
    null,
    )

from deform.widget import Widget
import cgi

class EsgSearchWidget(Widget):
    def serialize(self, field, cstruct, readonly=False):
        if cstruct is null:
            cstruct = u''
        return '<input type="text" value="%s">' % cgi.escape(cstruct)

    def deserialize(self, field, pstruct):
        if pstruct is null:
            return null
        return pstruct

    def handle_error(self, field, error):
        if field.error is None:
            field.error = error
        for e in error.children:
            for num, subfield in enumerate(field.children):
                if e.pos == num:
                    subfield.widget.handle_error(subfield, e)