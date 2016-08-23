from pyramid_celery import celery_app as app

from birdfeeder import feed_from_thredds, clear

from phoenix.db import mongodb

from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)


@app.task(bind=True)
def index_thredds(self, url, maxrecords=-1, depth=2):
    registry = app.conf['PYRAMID_REGISTRY']
    db = mongodb(registry)
    task = dict(task_id=self.request.id, url=url, status='started')
    db.tasks.save(task)
    service = registry.settings.get('solr.url')
    try:
        feed_from_thredds(service=service, catalog_url=url, depth=depth, maxrecords=maxrecords, batch_size=50000)
        task['status'] = 'success'
    except:
        task['status'] = 'failure'
        raise
    finally:
        db.tasks.update({'url': task['url']}, task)


@app.task(bind=True)
def clear_index(self):
    registry = app.conf['PYRAMID_REGISTRY']
    db = mongodb(registry)
    service = registry.settings.get('solr.url')
    clear(service=service)
    db.tasks.drop()
