from UserDict import DictMixin
from StringIO import StringIO

from deform.interfaces import FileUploadTempStore
import colander

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

class LocalTempStore(DictMixin):
    """
    A temporary storage for file uploads

    File uploads are stored in the local file storage so that you don't need
    to upload your file again if validation of another schema node
    fails.

    https://pythonhosted.org/pyramid_storage/
    """

    def __init__(self, request):
        self.request = request
        self.session = request.session

    def keys(self):
        logger.debug("keys")
        return [k for k in self.session.keys() if not k.startswith('_')]

    def __setitem__(self, name, value):
        logger.debug("setitem %s", name)
        value = value.copy()
        fp = value.pop('fp')
        value['stored_filename'] = self.request.storage.save_file(fp, value['filename'])
        self.session[name] = value

    def __getitem__(self, name):
        value = self.session[name].copy()
        value['path'] = self.request.storage.path(value['stored_filename'])
        #value['url'] = self.request.storage.url(value['stored_filename'])
        value['url'] = 'file://{path}'.format(path=self.request.storage.path(value['stored_filename']))
        logger.debug("getitem %s, path=%s, url=%s", name, value['path'], value['url'])
        return value

    def __delitem__(self, name):
        logger.debug("delitem %s", name)
        value = self.session[name]
        self.request.storage.delete(value['stored_filename'])
        del self.session[name]
        
    def preview_url(self, name):
        return None
    

class SessionTempStore(DictMixin):
    """
    A temporary storage for file uploads

    File uploads are stored in the session so that you don't need
    to upload your file again if validation of another schema node
    fails.

    http://kotti.pylonsproject.org/
    """

    def __init__(self, request):
        self.session = request.session

    def keys(self):
        return [k for k in self.session.keys() if not k.startswith('_')]

    def __setitem__(self, name, value):
        value = value.copy()
        fp = value.pop('fp')
        value['file_contents'] = fp.read()
        fp.seek(0)
        self.session[name] = value

    def __getitem__(self, name):
        value = self.session[name].copy()
        value['fp'] = StringIO(value.pop('file_contents'))
        return value

    def __delitem__(self, name):
        del self.session[name]

    @staticmethod
    def preview_url(name):
        return None


class FileSizeLimitValidator(object):
    """
    File size limit validator.

    You can configure the maximum size by setting the max_size
    option to the maximum number of megabytes that you want to allow.
    """
    def __init__(self, max_size):
        self.max_size = max_size

    def __call__(self, node, value):
        value['fp'].seek(0, 2)
        size = value['fp'].tell()
        value['fp'].seek(0)
        if size > int(self.max_size) * 1024 * 1024:
            msg = 'Maximum file size: {size}MB'.format(size=self.max_size)
            raise colander.Invalid(node, msg)
    
   

    

