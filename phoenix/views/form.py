from deform.interfaces import FileUploadTempStore
from UserDict import DictMixin
from StringIO import StringIO

import colander

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
    A temporary storage for file uploads

    File uploads are stored in the session so that you don't need
    to upload your file again if validation of another schema node
    fails.
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


def validate_file_size_limit(node, value):
    """
    File size limit validator.

    You can configure the maximum size by setting the kotti.max_file_size
    option to the maximum number of bytes that you want to allow.
    """

    value['fp'].seek(0, 2)
    size = value['fp'].tell()
    value['fp'].seek(0)
    #max_size = get_settings()['kotti.max_file_size']
    max_size = 2
    if size > int(max_size) * 1024 * 1024:
        msg = _('Maximum file size: ${size}MB', mapping={'size': max_size})
        raise colander.Invalid(node, msg)

