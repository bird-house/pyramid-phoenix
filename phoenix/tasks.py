from pyramid_celery import celery_app as app
from phoenix.models import mongodb

@app.task
def execute(email, url, identifier, inputs, outputs, workflow=False, keywords=None):
    from owslib.wps import WebProcessingService
    wps = WebProcessingService(url=url, skip_caps=True)
    execution = wps.execute(identifier, inputs=inputs, output=outputs)
    db = mongodb(app.conf['PYRAMID_REGISTRY'])
    from phoenix.models import add_job, update_job
    job = add_job(
        db = db,
        email = email,
        workflow = workflow,
        title = execution.process.title,
        wps_url = execution.serviceInstance,
        status_location = execution.statusLocation,
        abstract = execution.process.abstract,
        keywords = keywords)
    while not execution.isComplete():
        execution.checkStatus(sleepSecs=2)
        print execution.getStatus()
        update_job(db, job)
    return execution.getStatus()
