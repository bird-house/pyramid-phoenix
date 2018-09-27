import os
import shutil
import tempfile
import requests
import re
import six
from lxml import etree
from io import BytesIO
import OpenSSL
from dateutil import parser as date_parser

from pyramid_storage.interfaces import IFileStorage

from pyesgf.logon import LogonManager, ESGF_CREDENTIALS

from phoenix.db import mongodb

import logging
LOGGER = logging.getLogger(__name__)


def save_credentials(registry, userid, file=None, filename=None):
    # settings = registry.settings
    db = mongodb(registry)
    storage = registry.getUtility(IFileStorage)

    # store credentials.pem in storage
    storage_options = dict(
        folder="esgf_certs",
        extensions=('pem',),
        randomize=True)
    if file:
        stored_credentials = storage.save_file(
            file,
            filename=ESGF_CREDENTIALS,
            **storage_options)
    elif filename:
        stored_credentials = storage.save_filename(
            filename,
            **storage_options)
    else:
        raise Exception("No credentials to save. Use file or filename parameter.")
    # get cert infos
    infos = cert_infos(storage.path(stored_credentials))

    # update database
    user = db.users.find_one({'identifier': userid})
    user['openid'] = infos.get('openid')
    user['credentials'] = storage.url(stored_credentials)
    user['cert_expires'] = infos.get('expires_at')
    db.users.update({'identifier': userid}, user)


def logon(username=None, password=None, hostname=None, interactive=False, outdir=None):
    """
    Logon to MyProxy and fetch proxy certificate.
    """
    outdir = outdir or os.curdir
    lm = LogonManager(esgf_dir=outdir, dap_config=os.path.join(outdir, 'dodsrc'))
    lm.logoff()
    # TODO: fix encoding
    if six.PY2:
        hostname = hostname.encode('utf-8', 'ignore')
    # logon
    lm.logon(username=username, password=password, hostname=hostname,
             bootstrap=True, update_trustroots=False, interactive=interactive)
    return os.path.join(outdir, ESGF_CREDENTIALS)


def cert_infos(filename):
    # expires = None
    with open(filename) as fh:
        data = fh.read()
        cert = OpenSSL.crypto.load_certificate(OpenSSL.SSL.FILETYPE_PEM, data)
        expires_at = date_parser.parse(cert.get_notAfter()).replace(microsecond=0).isoformat()
        openid = dict(cert.get_subject().get_components()).get('CN')
    return dict(expires_at=expires_at, openid=openid)
