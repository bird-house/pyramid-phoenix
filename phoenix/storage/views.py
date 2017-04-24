import os
import shutil

from cgi import FieldStorage

from pyramid.view import view_config
from pyramid.response import FileResponse

from pyramid_storage.exceptions import FileNotAllowed

import logging
LOGGER = logging.getLogger(__name__)


@view_config(route_name='download_storage')
def download(request):
    filename = request.matchdict.get('filename')
    return FileResponse(request.storage.path(filename))


@view_config(route_name='upload', renderer='json', request_method="POST", xhr=True, accept="application/json")
def upload(request):
    result = {"success": False}
    if 'qqfile' in request.POST:
        try:
            handle_upload(request, request.POST)
            filename = os.path.join(request.POST['qquuid'], request.POST['qqfilename'])
            result = {'success': True, 'filename': filename}
        except FileNotAllowed:
            result = {"success": False, 'error': "Filename extension not allowed", "preventRetry": True}
        except Exception:
            result = {"success": False, 'error': "Upload failed"}
    return result


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
        save_chunk(fs.file, dest)

        # If the last chunk has been sent, combine the parts.
        if int(attrs['qqtotalparts']) - 1 == int(attrs['qqpartindex']):
            filename = os.path.join(dest_folder, attrs['qquuid'], attrs['qqfilename'])
            combine_chunks(
                int(attrs['qqtotalparts']),
                source_folder=os.path.dirname(dest),
                dest=filename)
            save_upload(request, filename=filename, folder=attrs['qquuid'])
            shutil.rmtree(dest_folder)
    else:  # not chunked
        save_upload(request, fs=fs, filename=attrs['qqfilename'], folder=attrs['qquuid'])


def save_upload(request, filename, fs=None, folder=None):
    LOGGER.debug("save: filename=%s, fs=%s", filename, fs)
    if not fs:
        stored_filename = request.storage.save_filename(filename, folder=folder)
    else:
        stored_filename = request.storage.save_file(fs.file, filename=filename, folder=folder)
    return stored_filename


def save_chunk(fs, path):
    """
    Save an uploaded chunk.

    Chunks are stored in chunks/
    """
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    with open(path, 'wb+') as destination:
        destination.write(fs.read())


def combine_chunks(total_parts, source_folder, dest):
    """
    Combine a chunked file into a whole file again. Goes through each part,
    in order, and appends that part's bytes to another destination file.

    Chunks are stored in chunks/
    """
    if not os.path.exists(os.path.dirname(dest)):
        os.makedirs(os.path.dirname(dest))

    with open(dest, 'wb+') as destination:
        for i in xrange(int(total_parts)):
            part = os.path.join(source_folder, str(i))
            with open(part, 'rb') as source:
                destination.write(source.read())
