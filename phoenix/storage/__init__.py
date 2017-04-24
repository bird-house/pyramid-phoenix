import os
import uuid

import logging
LOGGER = logging.getLogger(__name__)


def includeme(config):
    # settings = config.registry.settings
    LOGGER.debug('Adding storage ...')

    config.include('pyramid_storage')
    config.add_route('download_storage', 'download/storage/{filename:.*}')
    config.add_route('upload', 'upload')
