import os
import shutil
import tempfile
import requests
import re
from lxml import etree
from io import BytesIO
import OpenSSL
from dateutil import parser as date_parser

from pyesgf.logon import LogonManager, ESGF_CREDENTIALS

from pyramid_storage.interfaces import IFileStorage
from pyramid_celery import celery_app as app

from phoenix.db import mongodb

from celery.utils.log import get_task_logger
LOGGER = get_task_logger(__name__)


@app.task(bind=True)
def esgf_logon(self, userid, url, openid, password):
    LOGGER.debug("esgf_logon, url=%s", url)
    result = {'status': "Running"}
    registry = app.conf['PYRAMID_REGISTRY']
    settings = registry.settings
    db = mongodb(registry)
    storage = registry.getUtility(IFileStorage)

    try:
        # need temp folder for outputs
        if not os.path.isdir(settings.get('phoenix.workdir')):
            os.makedirs(settings.get('phoenix.workdir'), mode=0700)
        outdir = tempfile.mkdtemp(prefix='phoenix-', dir=settings.get('phoenix.workdir'))
        # use myproxy logon to get credentials
        credentials = myproxy_logon_with_openid(openid=openid, password=password, outdir=outdir)
        cert_expires = cert_infos(credentials).get('expires')
        # store credentials.pem in storage
        stored_credentials = storage.save_filename(credentials, folder="esgf_certs",
                                                   extensions=('pem',), randomize=True)
        # remove tempfolder
        shutil.rmtree(outdir)

        user = db.users.find_one({'identifier': userid})
        user['openid'] = openid
        user['credentials'] = storage.url(stored_credentials)
        user['cert_expires'] = cert_expires
        db.users.update({'identifier': userid}, user)
    except Exception as err:
        LOGGER.exception("esgf logon failed.")
        result['status'] = 'Failed'
        result['message'] = err.message
    else:
        result['status'] = 'Success'
    return result


def myproxy_logon_with_openid(openid, password=None, interactive=False, outdir=None):
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
        expires = date_parser.parse(cert.get_notAfter())
    return dict(expires=expires)
