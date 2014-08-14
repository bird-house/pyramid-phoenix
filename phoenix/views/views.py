from pyramid.view import (
    view_config,
    forbidden_view_config,
    notfound_view_config
    )
from pyramid.response import Response
from pyramid.events import subscriber, BeforeRender

import logging
logger = logging.getLogger(__name__)

@notfound_view_config(renderer='phoenix:templates/404.pt')
def notfound(request):
    """This special view just renders a custom 404 page. We do this
    so that the 404 page fits nicely into our global layout.
    """
    return {}

@forbidden_view_config(renderer='phoenix:templates/forbidden.pt')
def forbidden(request):
    request.response.status = 403
    return dict(message=None)

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


