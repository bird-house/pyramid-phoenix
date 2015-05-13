from pyramid_celery import celery_app as app

@app.task
def add(x, y):
    print x+y


