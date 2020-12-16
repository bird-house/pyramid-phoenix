from glob import glob
from io import BytesIO
import logging
from os import makedirs, path, remove

import colander
from deform.interfaces import FileUploadTempStore
from deform.widget import filedict


LOGGER = logging.getLogger("PHOENIX")


class FileUploadStore(FileUploadTempStore):
    """
    This class implements the deform.interfaces.FileUploadTempStore.
    """

    storage_dir = None
    max_size = None

    def __init__(self, storage_dir, max_size):
        self.storage_dir = storage_dir
        self.max_size = max_size
        super().__init__()

    def get(self, name, default=None):
        file_name = self._get_full_file_name(name)
        if file_name is None:
            return default

        data = filedict()
        with open(file_name, "rb") as reader:
            data["fp"] = BytesIO(reader.read())

        data["uid"] = self._get_uid(name)
        data["filename"] = path.basename(file_name)
        data["preview_url"] = None
        return data

    def __getitem__(self, name):
        data = self.get(name)
        if data is None:
            raise KeyError(name)
        return data

    def __setitem__(self, name, value):
        """
        Write the data to a file.
        """
        # first check it is not to big
        value["fp"].seek(0, 2)
        size = value["fp"].tell()
        value["fp"].seek(0)
        if size > int(self.max_size) * 1024 * 1024:
            msg = "Maximum file size: {size}MB".format(size=self.max_size)
            #            raise Exception(msg)
            raise colander.Invalid(None, msg)

        file_dir = self._file_dir(name)

        if path.isdir(file_dir):
            # this must be an update, get rid of the old file
            files = glob(path.join(file_dir, "*"))
            for file in files:
                try:
                    remove(file)
                    LOGGER.debug("Deleted file {}".format(file))
                except OSError as e:
                    LOGGER.error("Error deleting {}. {}".format(file, e))

        makedirs(file_dir, exist_ok=True)
        file_path = path.join(file_dir, value.get("filename"))

        with open(file_path, "wb") as writer:
            writer.write(value.get("fp").read())

        LOGGER.info("Written file: {}".format(file_path))

    def __contains__(self, name):
        """
        Return 'True' if a file exists in the directory.
        """
        file_path = self._file_dir(name)
        if not path.isdir(file_path):
            return False

        # We only know the directory name
        files = glob(path.join(file_path, "*"))
        if len(files) == 0:
            return False

        return True

    def preview_url(self, name):
        return None

    def _file_dir(self, name):
        return path.join(self.storage_dir, name)

    def _get_full_file_name(self, name):
        """
        The name might be the full path to a file or a UID.
        """
        if path.isfile(name):
            # nothing to do
            return name

        # we assume we have a UID
        file_path = self._file_dir(name)
        if not path.isdir(file_path):
            return None

        # We only know the directory name
        files = glob(path.join(file_path, "*"))
        if len(files) == 0:
            return None

        # There should only be one file
        return files[0]

    def _get_uid(self, name):
        if not name.startswith(self.storage_dir):
            return name
        uid = path.dirname(name)
        uid = path.relpath(uid, start=self.storage_dir)
        return uid
