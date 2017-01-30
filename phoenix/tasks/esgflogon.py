import os
import shutil
import tempfile

from pyramid_storage.interfaces import IFileStorage
from pyramid_celery import celery_app as app

from phoenix.db import mongodb
from phoenix.esgf.logon import logon_with_openid, cert_infos

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
        credentials = logon_with_openid(openid=openid, password=password, outdir=outdir)
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
