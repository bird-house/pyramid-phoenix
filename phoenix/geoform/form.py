import os

import colander
from pyramid.security import authenticated_userid
from pyramid.compat import urlparse


class BBoxValidator(object):
    """
    Bounding-Box validator which succeeds if the bbox value has the format
    :attr:`minx,miny,maxx,maxy` and values are in range (``-180 <= x <=180``, ``-90 <= y <=90``).
    """
    def __call__(self, node, value):
        try:
            minx, miny, maxx, maxy = [float(val) for val in value.split(',', 3)]
        except Exception:
            raise colander.Invalid(node, "Could not parse BBox.")
        else:
            if minx > maxx:
                raise colander.Invalid(node, "MinX greater than MaxX")
            if miny > maxy:
                raise colander.Invalid(node, "MinY greater than MaxY")
            if minx < -360 or maxx > 360:
                raise colander.Invalid(node, "X values cannot exceed [-360, 360].")
            if miny < -90 or maxy > 90:
                raise colander.Invalid(node, "Y values cannot exceed [-90, 90].")
            if (maxx - minx) > 360:
                raise colander.Invalid(node, "Cannot select a longitude range greater than 360.")


class URLValidator(object):
    """
    URL validator which can configured with allowed URL schemes.
    """
    def __init__(self, allowed_schemes=None):
        self.allowed_schemes = allowed_schemes or ['http', 'https']

    def __call__(self, node, value):
        try:
            parsed_url = urlparse.urlparse(value)
        except Exception:
            raise colander.Invalid(node, "Invalid URL.")
        else:
            if parsed_url.scheme not in self.allowed_schemes:
                raise colander.Invalid(node, "URL scheme {} is not allowed.".format(parsed_url.scheme))
            if not parsed_url.netloc:
                raise colander.Invalid(node, "Invalid URL.")
            if '..' in parsed_url.path:
                raise colander.Invalid(node, "Invalid URL.")


class TextValidator(object):
    """
    """
    def __init__(self, restricted_chars=None):
        self.restricted_chars = restricted_chars or ["\\", "#", ";", "&", "!", "<", ">"]

    def __call__(self, node, value):
        try:
            normalized_value = str(value).strip()
        except Exception:
            raise colander.Invalid(node, "Invalid value.")
        else:
            if not normalized_value:
                raise colander.Invalid(node, "Invalid value ... empty.")
            for char in self.restricted_chars:
                if char in normalized_value:
                    raise colander.Invalid(node, "Invalid value ... contains restricted characters.")


class VocabValidator(object):
    """
    Validate values against a vocabulary.
    """
    def __init__(self, vocab):
        self.vocab = vocab

    def __call__(self, node, values):
        if isinstance(values, set):
            values = list(values)
        if not isinstance(values, list):
            values = [values]

        for value in values:
            try:
                normalized_value = str(value).strip()
            except Exception:
                raise colander.Invalid(node, "Invalid value.")
            if not normalized_value:
                raise colander.Invalid(node, "Invalid value ... empty.")
            if value not in self.vocab:
                raise colander.Invalid(
                    node, "Invalid value ... value not in list of allowed values.")


class FileUploadValidator(colander.All):
    """
    Runs all validators for file upload checks.
    """
    def __init__(self, storage, max_size):
        self.validators = [FileFormatAllowedValidator(storage), FileSizeLimitValidator(storage, max_size)]


class FileFormatAllowedValidator(object):
    """
    File format extension is allowed.

    https://pythonhosted.org/pyramid_storage/
    """
    def __init__(self, storage):
        self.storage = storage

    def __call__(self, node, value):
        if not self.storage.filename_allowed(value['filename']):
            msg = 'File format is not allowed: {filename}'.format(filename=value['filename'])
            raise colander.Invalid(node, msg)


class FileSizeLimitValidator(object):
    """
    File size limit validator.

    You can configure the maximum size by setting the max_size
    option to the maximum number of megabytes that you want to allow.
    """
    def __init__(self, storage, max_size=2):
        self.storage = storage
        self.max_size = max_size

    def __call__(self, node, value):
        value['fp'].seek(0, 2)
        size = value['fp'].tell()
        value['fp'].seek(0)
        if size > int(self.max_size) * 1024 * 1024:
            msg = 'Maximum file size: {size}MB'.format(size=self.max_size)
            raise colander.Invalid(node, msg)
