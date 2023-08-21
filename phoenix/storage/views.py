import os
import shutil

from cgi import FieldStorage

from pyramid.view import view_config
from pyramid.response import FileResponse

from pyramid_storage.exceptions import FileNotAllowed

import logging
LOGGER = logging.getLogger("PHOENIX")


@view_config(route_name='download_storage')
def download(request):
    filename = request.matchdict.get('filename')
    return FileResponse(request.storage.path(filename))


@view_config(route_name='upload_delete', renderer='json', request_method="DELETE", xhr=True, accept="application/json")
def delete(request):
    """
    A DELETE request. If found, deletes a file with the corresponding
    UUID from the servers filesystem.
    """
    try:
        handle_delete(request, uuid=request.matchdict.get('uuid'))
        result = {"success": True}
    except Exception as e:
        result = {"success": False, "error": e.message}
    return result


@view_config(route_name='upload', renderer='json', request_method="POST", xhr=True)  # , accept="multipart/form-data")
def upload(request):
    result = {"success": False}
    LOGGER.warn(request.POST)
    if 'file' in request.POST:
        try:
            return handle_upload(request, request.POST)
        except FileNotAllowed:
            result = {"success": False, 'error': "Filename extension not allowed", "preventRetry": True}
        except Exception as e:
            result = {"success": False, 'error': e.message}
    return result


def handle_delete(request, uuid):
    """ Handles a filesystem delete based on UUID."""
    location = request.storage.path(uuid)
    shutil.rmtree(location)


def handle_upload(request, attrs):
    """
    Handle a chunked or non-chunked upload.
    """
    fs = attrs['file']
    # We can fail hard, as somebody is trying to cheat on us if that fails.
    assert isinstance(fs, FieldStorage)

    # extension allowed?
    # request.storage.filename_allowed(attrs['qqfilename'])

    # Chunked?
    if 'dztotalchunkcount' in attrs and int(attrs['dztotalchunkcount']) > 1:
        LOGGER.warn(f"chunked, {fs.name}")
        dest_folder = os.path.join(request.storage.path('chunks'), attrs['dzuuid'])
        dest = os.path.join(dest_folder, "parts", str(attrs['dzchunkindex']))
        save_chunk(fs.file, dest)

        # If the last chunk has been sent, combine the parts.
        if int(attrs['dztotalchunkcount']) - 1 == int(attrs['dzchunkindex']):
            filename = os.path.join(dest_folder, attrs['dzuuid'], fs.name)  # attrs['qqfilename'])
            combine_chunks(
                int(attrs['dztotalchunkcount']),
                source_folder=os.path.dirname(dest),
                dest=filename)
            request.storage.save_filename(filename=filename, folder=attrs['dzuuid'])
            shutil.rmtree(dest_folder)
    else:  # not chunked
        LOGGER.warn(f"not chunked, {fs.name}, {attrs}")
        filename = "test.nc"
        request.storage.save_file(
            fs.file, 
            filename="test.nc",  # attrs['qqfilename'], 
            folder="test"  # attrs['dzuuid']
        )
    return {'success': True, 'filename': filename}


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
        for i in range(int(total_parts)):
            part = os.path.join(source_folder, str(i))
            with open(part, 'rb') as source:
                destination.write(source.read())
