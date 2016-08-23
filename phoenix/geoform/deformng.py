"""
This module contains code form the next deform version only available on github:

https://github.com/Pylons/deform
"""

from colander import (
    String,
    string_types,
)

from deform.compat import (
    text_,
    )

_BLANK = text_('')


class _PossiblyEmptyString(String):
    def deserialize(self, node, cstruct):
        if cstruct == '':
            return _BLANK               # String.deserialize returns null
        return super(_PossiblyEmptyString, self).deserialize(node, cstruct)


class StrippedString(_PossiblyEmptyString):
    def deserialize(self, node, cstruct):
        appstruct = super(StrippedString, self).deserialize(node, cstruct)
        if isinstance(appstruct, string_types):
            appstruct = appstruct.strip()
        return appstruct
