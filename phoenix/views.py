import os

from pyramid.view import view_config, view_defaults
from pyramid.view import notfound_view_config
from pyramid.response import Response
from pyramid.events import subscriber, BeforeRender

from phoenix.utils import get_user

import logging
logger = logging.getLogger(__name__)

_here = os.path.dirname(__file__)

# favicon static/favicon.ico
_favicon = open(os.path.join(
                _here, 'static', 'favicon.ico')).read()
_favicon_response = Response(content_type='image/x-icon', body=_favicon)

# robots static/robots.txt
_robots = open(os.path.join(
               _here, 'static', 'robots.txt')).read()
_robots_response = Response(content_type='text/plain', body=_robots)


class MyView(object):
    def __init__(self, request, name, title, description=None):
        self.request = request
        self.session = self.request.session
        self.context = self.request.context
        self.name = name
        self.title = title
        self.description = description
        # TODO: refactor db access
        self.userdb = self.request.db.users

        # set breadcrumbs
        for item in self.breadcrumbs():
            lm = self.request.layout_manager
            lm.layout.add_breadcrumb(
                route_path=item.get('route_path'),
                title=item.get('title'))

    def get_user(self):
        return get_user(self.request)

    def breadcrumbs(self):
        return [dict(route_path=self.request.route_path("home"), title="Home")]


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
    response = Response('Ooops, something went wrong. Check the log files.')
    response.status_int = 500
    return response


@view_config(name='favicon.ico')
def favicon_view(request):
    return _favicon_response


@view_config(name='robots.txt')
def robotstxt_view(request):
    return _robots_response


@view_defaults(permission='view', layout='default')
class Home(object):
    def __init__(self, request):
        self.request = request
        self.session = self.request.session

    @view_config(route_name='home', renderer='phoenix:templates/home.pt')
    def view(self):
        from phoenix.utils import pinned_processes
        processes = pinned_processes(self.request)
        return dict(processes=processes)
