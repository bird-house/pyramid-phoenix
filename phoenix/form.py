import os
from UserDict import DictMixin

import colander
from pyramid.security import authenticated_userid

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
        folder = authenticated_userid(self.request)
        relpath = os.path.join(folder, value['filename'])
        if self.request.storage.exists(relpath):
            self.request.storage.delete(relpath)
        value['filename'] = self.request.storage.save_file(fp, value['filename'], folder=folder)
        logger.debug("setitem %s %s", name, value)
        self.session[name] = value

    def __getitem__(self, name):
        return self.session[name].copy()

    def __delitem__(self, name):
        del self.session[name]
        
    def preview_url(self, name):
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
    
   

    

