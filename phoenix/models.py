# TODO: refactor usage of mongodb etc ...

import uuid
import datetime

import logging

log = logging.getLogger(__name__)

from helpers import mongodb_conn

def mongodb_add_job(request, user_id, identifier, wps_url, execution):
    conn = mongodb_conn(request)
    conn.phoenix_db.jobs.save(dict(
        user_id= user_id, 
        uuid=uuid.uuid4().get_hex(),
        identifier=identifier,
        service_url=wps_url,
        status_location=execution.statusLocation,
        status = execution.status,
        start_time = datetime.datetime.now(),
        end_time = datetime.datetime.now(),
      ))
    log.debug('count jobs = %s', conn.phoenix_db.jobs.count())
