from phoenix import models

import logging
logger = logging.getLogger(__name__)

class MyView(object):
    def __init__(self, request, name, title, description=None):
        self.request = request
        self.session = self.request.session
        self.name = name
        self.title = title
        self.description = description
        # TODO: refactor db access
        self.db = self.request.db
        self.userdb = self.request.db.users

        # set breadcrumbs
        for item in self.breadcrumbs():
            lm = self.request.layout_manager
            lm.layout.add_breadcrumb(
                route_path=item.get('route_path'),
                title=item.get('title'))

    def get_user(self):
        return models.get_user(self.request)

    def breadcrumbs(self):
        return [dict(route_path=self.request.route_path("home"), title="Home")]

from pyramid.view import (
    view_config,
    notfound_view_config
    )
from pyramid.response import Response
from pyramid.events import subscriber, BeforeRender

@notfound_view_config(renderer='phoenix:templates/404.pt')
def notfound(request):
    """This special view just renders a custom 404 page. We do this
    so that the 404 page fits nicely into our global layout.
    """
    return {}

@subscriber(BeforeRender)
def add_global(event):
    event['message_type'] = 'alert-info'
    event['message'] = ''

@view_config(context=Exception)
def unknown_failure(request, exc):
    #import traceback
    logger.exception('unknown failure')
    #msg = exc.args[0] if exc.args else ""
    #response =  Response('Ooops, something went wrong: %s' % (traceback.format_exc()))
    response =  Response('Ooops, something went wrong. Check the log files.')
    response.status_int = 500
    return response

