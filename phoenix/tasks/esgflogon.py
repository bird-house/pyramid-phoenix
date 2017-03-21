import os
import shutil
import tempfile

from pyramid_celery import celery_app as app

from phoenix.esgf.logon import logon, save_credentials

from celery.utils.log import get_task_logger
LOGGER = get_task_logger(__name__)


@app.task(bind=True)
def esgf_logon(self, userid, hostname, username, password):
    result = {'status': "Running"}
    registry = app.conf['PYRAMID_REGISTRY']
    settings = registry.settings

    try:
        # need temp folder for outputs
        if not os.path.isdir(settings.get('phoenix.workdir')):
            os.makedirs(settings.get('phoenix.workdir'), mode=0700)
        outdir = tempfile.mkdtemp(prefix='phoenix-', dir=settings.get('phoenix.workdir'))
        # use myproxy logon to get credentials
        credentials = logon(username=username, password=password, hostname=hostname,
                            outdir=outdir)

        # store credentials
        save_credentials(registry, userid, filename=credentials)

        # remove tempfolder
        shutil.rmtree(outdir)
    except Exception as err:
        LOGGER.exception("esgf logon failed.")
        result['status'] = 'Failed'
        result['message'] = err.message
    else:
        result['status'] = 'Success'
    return result
