from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.security import authenticated_userid

import logging
logger = logging.getLogger(__name__)

@view_config(route_name='remove_myjobs', permission='submit', layout='default')
def remove_myjobs(request):
    count = request.db.jobs.find({'email': authenticated_userid(request)}).count()
    request.db.jobs.remove({'email': authenticated_userid(request)})
    request.session.flash("%d Jobs deleted." % count, queue='info')
    return HTTPFound(location = request.route_path('monitor'))

@view_config(route_name='remove_all_jobs', permission='admin', layout='default')
def remove_all(request):
    count = request.db.jobs.count()
    request.db.jobs.drop()
    request.session.flash("%d Jobs deleted." % count, queue='info')
    return HTTPFound(location=request.route_path('monitor'))
