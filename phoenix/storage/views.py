import os
import shutil

from cgi import FieldStorage

from pyramid.view import view_config
from pyramid.response import FileResponse

from pyramid_storage.exceptions import FileNotAllowed

from phoenix.storage import save_upload, save_chunk, combine_chunks

import logging
LOGGER = logging.getLogger(__name__)


@view_config(route_name='download_storage')
def download(request):
    filename = request.matchdict.get('filename')
    #filename = request.params['filename']
    LOGGER.debug("download: %s", request.storage.path(filename))
    return FileResponse(request.storage.path(filename))


def handle_upload(request, attrs):
    """
    Handle a chunked or non-chunked upload.

    See example code:
    https://github.com/FineUploader/server-examples/blob/master/python/flask-fine-uploader/app.py
    """
    fs = attrs['qqfile']
    # We can fail hard, as somebody is trying to cheat on us if that fails.
    assert isinstance(fs, FieldStorage)

    # extension allowed?
    request.storage.filename_allowed(attrs['qqfilename'])

    # Chunked?
    if 'qqtotalparts' in attrs and int(attrs['qqtotalparts']) > 1:
        dest_folder = os.path.join(request.storage.path('chunks'), attrs['qquuid'])
        dest = os.path.join(dest_folder, "parts", str(attrs['qqpartindex']))
        LOGGER.debug('Chunked upload received')
        save_chunk(fs.file, dest)

        # If the last chunk has been sent, combine the parts.
        if int(attrs['qqtotalparts']) - 1 == int(attrs['qqpartindex']):
            filename = os.path.join(dest_folder, attrs['qqfilename'])
            combine_chunks(
                int(attrs['qqtotalparts']),
                source_folder=os.path.dirname(dest),
                dest=filename)

            save_upload(request, filename=filename)

            shutil.rmtree(dest_folder)
    else:  # not chunked
        save_upload(request, fs=fs, filename=attrs['qqfilename'])


@view_config(route_name='upload', renderer='json', request_method="POST", xhr=True, accept="application/json")
def upload(request):
    LOGGER.debug("upload post=%s", request.POST)
    result = {"success": False}
    if 'qqfile' in request.POST:
        try:
            handle_upload(request, request.POST)
            result = {'success': True}
        except FileNotAllowed:
            msg = "Filename extension not allowed"
            LOGGER.warn(msg)
            result = {"success": False, 'error': msg, "preventRetry": True}
        except Exception:
            msg = "Upload failed"
            LOGGER.exception(msg)
            result = {"success": False, 'error': msg}
    return result
