import os

import logging
logger = logging.getLogger(__name__)


def includeme(config):
    # settings = config.registry.settings
    logger.debug('Adding storage ...')

    config.include('pyramid_storage')
    config.add_route('download_storage', 'download/storage/{filename:.*}')
    config.add_route('upload', 'upload')

# upload helpers


def save_upload(request, filename, fs=None):
    logger.debug("save_upload: filename=%s, fs=%s", filename, fs)
    if request.storage.exists(os.path.basename(filename)):
        request.storage.delete(os.path.basename(filename))
    if fs is None:
        stored_filename = request.storage.save_filename(filename)
        logger.debug('saved chunked file to upload storage %s', stored_filename)
    else:
        stored_filename = request.storage.save_file(fs.file, filename=filename)
        logger.debug('saved file to upload storage %s', stored_filename)


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
    Combine a chunked file into a whole file again. Goes through each part
    , in order, and appends that part's bytes to another destination file.

    Chunks are stored in chunks/
    """

    logger.debug("Combining chunks: %s", source_folder)

    if not os.path.exists(os.path.dirname(dest)):
        os.makedirs(os.path.dirname(dest))

    with open(dest, 'wb+') as destination:
        for i in xrange(int(total_parts)):
            part = os.path.join(source_folder, str(i))
            with open(part, 'rb') as source:
                destination.write(source.read())
        logger.debug("Combined: %s", dest)
