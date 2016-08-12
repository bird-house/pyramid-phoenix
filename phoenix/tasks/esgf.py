from pyramid_celery import celery_app as app

from owslib.wps import WebProcessingService, monitorExecution

from phoenix.db import mongodb
from phoenix.tasks import wps_headers

from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)


@app.task(bind=True)
def esgf_logon(self, userid, url, openid, password):
    registry = app.conf['PYRAMID_REGISTRY']
    db = mongodb(registry)

    inputs = [
        ('openid', openid),
        ('password', password)]
    outputs = [('output', True), ('expires', False)]

    wps = WebProcessingService(url=url, skip_caps=True, verify=False, headers=wps_headers(userid))
    execution = wps.execute(identifier="esgf_logon", inputs=inputs, output=outputs)
    monitorExecution(execution)

    if execution.isSucceded():
        credentials = execution.processOutputs[0].reference
        cert_expires = execution.processOutputs[1].data[0]
        user = db.users.find_one({'identifier': userid})
        user['openid'] = openid
        user['credentials'] = credentials
        user['cert_expires'] = cert_expires
        db.users.update({'identifier': userid}, user)
    return execution.status
