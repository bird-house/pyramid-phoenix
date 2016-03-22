import os
from UserDict import DictMixin

import colander
from pyramid.security import authenticated_userid

from pyramid_storage.exceptions import FileNotAllowed

import logging
logger = logging.getLogger(__name__)


class MemoryTempStore(dict):
    """
    A temporay storage for file uploads.

    File uploads are stored in memory (dict).

    http://docs.pylonsproject.org/projects/deform/en/latest/interfaces.html
    """
    def __init__(self, request):
        self.request = request
    
    def preview_url(self, name):
        return None

class FileUploadTempStore(DictMixin):
    """
    A temporary storage for file uploads.

    File uploads are stored in the local file storage and referenced in session
    so that you don't need to upload your file again if validation of another
    schema node fails.

    https://pythonhosted.org/pyramid_storage/

    See deform.interfaces.FileUploadTempStore

    See also FileUploadTempStore in Kotti: http://kotti.pylonsproject.org/
    """

    def __init__(self, request):
        self.request = request
        self.session = request.session

    def keys(self):
        return [k for k in self.session.keys() if not k.startswith('_')]

    def __setitem__(self, name, value):
        value = value.copy()
        fp = value.pop('fp')
        filename = self._filename(value)
        if self.request.storage.exists(filename):
            self.request.storage.delete(filename)
        try:
            value['filename'] = self.request.storage.save_file(fp, value['filename'], folder=self._folder())
            fp.seek(0, 2)
            value['size'] = fp.tell()
            fp.seek(0)
            logger.debug('saved file to upload storage: %s', value['filename'])
        except FileNotAllowed:
            logger.warn("File format is not allowed in storage: %s", value['filename'])
        logger.debug("setitem %s %s", name, value)
        self.session[name] = value
        
    def __getitem__(self, name):
        value = self.session[name].copy()
        if self.request.storage.exists(value['filename']):
            value['fp'] = open(self.request.storage.path(value['filename']), 'r')
        logger.debug("getitem %s", value)
        return value

    def __delitem__(self, name):
        logger.debug('delitem %s', name)
        del self.session[name]

    @staticmethod
    def preview_url(name):
        return None

    def _folder(self):
        return authenticated_userid(self.request)
    
    def _filename(self, value):
        return os.path.join(self._folder(), value['filename'])

class BBoxValidator(object):
    def __call__(self, node, value):
        try:
            minx, miny, maxx, maxy = [ float(val) for val in value.split(',', 3)]
        except:
            raise colander.Invalid(node, "Could not parse BBox.")
        else:
            if minx < 0 or minx > 180:
                raise colander.Invalid(node, "MinX out of range [0, 180].")
            if miny < -90 or miny > 90:
                raise colander.Invalid(node, "MinY out of range [-90, 90].")
            if maxx < 0 or maxx > 180:
                raise colander.Invalid(node, "MaxX out of range [0, 180].")
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
    
   

    

