import os
from cgi import FieldStorage

from pyramid.view import view_config, view_defaults
from pyramid.view import notfound_view_config
from pyramid.response import Response
from pyramid.response import FileResponse
from pyramid.events import subscriber, BeforeRender
from pyramid.security import authenticated_userid

from pyramid_storage.exceptions import FileNotAllowed

from phoenix.models import get_user

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
    response =  Response('Ooops, something went wrong. Check the log files.')
    response.status_int = 500
    return response

@view_config(route_name='download')
def download(request):
    filename = request.matchdict.get('filename')
    #filename = request.params['filename']
    return FileResponse(request.storage.path(filename))

@view_config(route_name='upload', renderer='json', request_method="POST", xhr=True, accept="application/json")
def upload(request):
    logger.debug("upload post=%s", request.POST)
    result = {'error': 'Could not upload files'}
    if 'qqfile' in request.POST:
        fs = request.POST['qqfile']
        # We can fail hard, as somebody is trying to cheat on us if that fails.
        assert isinstance(fs, FieldStorage)
        
        fid = request.POST.get('qquuid')
        logger.debug('uuid=%s', fid)
        filename = request.POST.get('qqfilename')
        logger.debug('filename=%s', filename)
        logger.debug('size=%s', request.POST.get('qqtotalfilesize'))
        #logger.debug('content type=%s', request.POST.get('content_type'))
        try:
            folder=authenticated_userid(request)
            filepath = os.path.join(folder, filename)
            if request.storage.exists(filepath):
                request.storage.delete(filepath)
            stored_filename = request.storage.save_file(fs.file, filename, folder=folder)
            logger.debug('saved file to upload storage: %s', stored_filename)
        except FileNotAllowed:
            msg = "File format is not allowed in storage: {0}".format(filename)
            logger.warn(msg)
            result = {'error': msg}
        else:
            result = {'success': True, 'uuid': fid}
    return result

@view_defaults(permission='view', layout='default')
class Home(object):
    def __init__(self, request):
        self.request = request
        self.session = self.request.session

    @view_config(route_name='home', renderer='phoenix:templates/home.pt')
    def view(self):
        return {}
