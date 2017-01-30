import os
import shutil
import tempfile
import requests
import re
from lxml import etree
from io import BytesIO
import OpenSSL
from dateutil import parser as date_parser

from pyramid_storage.interfaces import IFileStorage

from pyesgf.logon import LogonManager, ESGF_CREDENTIALS

from phoenix.db import mongodb

import logging
LOGGER = logging.getLogger(__name__)


def save_credentials(registry, userid, file=None, filename=None, openid=None):
    settings = registry.settings
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
    cert_expires = cert_infos(storage.path(stored_credentials)).get('expires')

    # update database
    user = db.users.find_one({'identifier': userid})
    if openid:
        user['openid'] = openid
    user['credentials'] = storage.url(stored_credentials)
    user['cert_expires'] = cert_expires
    db.users.update({'identifier': userid}, user)


def logon_with_openid(openid, password=None, interactive=False, outdir=None):
    """
    Tries to get MyProxy parameters from OpenID and calls :meth:`logon`.

    :param openid: OpenID used to login at ESGF node.
    """
    outdir = outdir or os.curdir
    username, hostname, port = parse_openid(openid)
    lm = LogonManager(esgf_dir=outdir, dap_config=os.path.join(outdir, 'dodsrc'))
    lm.logoff()
    lm.logon(username=username, password=password, hostname=hostname,
             bootstrap=True, update_trustroots=False, interactive=interactive)
    return os.path.join(outdir, ESGF_CREDENTIALS)


def parse_openid(openid, ssl_verify=False):
    """
    parse openid document to get myproxy service
    """
    XRI_NS = 'xri://$xrd*($v*2.0)'
    MYPROXY_URN = 'urn:esg:security:myproxy-service'
    ESGF_OPENID_REXP = r'https://.*/esgf-idp/openid/(.*)'
    MYPROXY_URI_REXP = r'socket://([^:]*):?(\d+)?'

    response = requests.get(openid, verify=ssl_verify)
    xml = etree.parse(BytesIO(response.content))

    hostname = None
    port = None
    username = None

    services = xml.findall('.//{%s}Service' % XRI_NS)
    for service in services:
        try:
            service_type = service.find('{%s}Type' % XRI_NS).text
        except AttributeError:
            continue

        # Detect myproxy hostname and port
        if service_type == MYPROXY_URN:
            myproxy_uri = service.find('{%s}URI' % XRI_NS).text
            mo = re.match(MYPROXY_URI_REXP, myproxy_uri)
            if mo:
                hostname, port = mo.groups()

    # If the OpenID matches the standard ESGF pattern assume it contains
    # the username, otherwise prompt or raise an exception
    mo = re.match(ESGF_OPENID_REXP, openid)
    if mo:
        username = mo.group(1)

    port = port or "7512"

    return username, hostname, port


def cert_infos(filename):
    expires = None
    with open(filename) as fh:
        data = fh.read()
        cert = OpenSSL.crypto.load_certificate(OpenSSL.SSL.FILETYPE_PEM, data)
        expires = date_parser.parse(cert.get_notAfter()).replace(microsecond=0).isoformat()
    return dict(expires=expires)
