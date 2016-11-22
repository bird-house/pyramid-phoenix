import os
from UserDict import DictMixin

import colander
from pyramid.security import authenticated_userid

from pyramid_storage.exceptions import FileNotAllowed

import logging
logger = logging.getLogger(__name__)


class BBoxValidator(object):
    def __call__(self, node, value):
        try:
            minx, miny, maxx, maxy = [float(val) for val in value.split(',', 3)]
        except:
            raise colander.Invalid(node, "Could not parse BBox.")
        else:
            if minx < -180 or minx > 180:
                raise colander.Invalid(node, "MinX out of range [-180, 180].")
            if miny < -90 or miny > 90:
                raise colander.Invalid(node, "MinY out of range [-90, 90].")
            if maxx < -180 or maxx > 180:
                raise colander.Invalid(node, "MaxX out of range [-180, 180].")
            if maxy < -90 or maxy > 90:
                raise colander.Invalid(node, "MaxY out of range [-90, 90].")
            if minx > maxx:
                raise colander.Invalid(node, "MinX greater than MaxX")
            if miny > maxy:
                raise colander.Invalid(node, "MinY greater than MaxY")


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
