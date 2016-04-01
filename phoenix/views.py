import os
import os.path
import shutil
from cgi import FieldStorage

from pyramid.view import view_config, view_defaults
from pyramid.view import notfound_view_config
from pyramid.response import Response
from pyramid.response import FileResponse
from pyramid.events import subscriber, BeforeRender
from pyramid.security import authenticated_userid

from pyramid_storage.exceptions import FileNotAllowed

from phoenix.models import get_user
from phoenix.utils import save_upload, combine_chunks

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

def handle_upload(request, fileattrs):
    """
    Handle a chunked or non-chunked upload.

    See example code:
    https://github.com/FineUploader/server-examples/blob/master/python/flask-fine-uploader/app.py
    """
    chunked = False
    
    fs = fileattrs['qqfile']
    # We can fail hard, as somebody is trying to cheat on us if that fails.
    assert isinstance(fs, FieldStorage)

    fid = fileattrs['qquuid']
       
    # Chunked?
    if int(fileattrs['qqtotalparts']) > 1:
        dest_folder = os.path.join(request.storage.path('chunks'), fileattrs['qquuid'])
        dest = os.path.join(dest_folder, fileattrs['qqfilename'], str(fileattrs['qqpartindex']))
        logger.info('Chunked upload received')
        save_upload(fs.file, dest)
        
        # If the last chunk has been sent, combine the parts.
        if int(fileattrs['qqtotalparts']) - 1 == int(fileattrs['qqpartindex']):
            logger.info('Combining chunks: %s' % os.path.dirname(dest))
            combine_chunks(int(fileattrs['qqtotalparts']),
                int(fileattrs['qqtotalfilesize']),
                source_folder=os.path.dirname(dest),
                dest=os.path.join(request.storage.path(authenticated_userid(request)), fileattrs['qqfilename']))
            logger.info('Combined')

            shutil.rmtree(dest_folder)
    else:
        folder=authenticated_userid(request)
        filename=fileattrs['qqfilename']
        filepath = os.path.join(folder, filename)
        if request.storage.exists(filepath):
            request.storage.delete(filepath)
        stored_filename = request.storage.save_file(fs.file, filename, folder=folder)
        logger.debug('saved file to upload storage: %s', stored_filename)

@view_config(route_name='upload', renderer='json', request_method="POST", xhr=True, accept="application/json")
def upload(request):
    logger.debug("upload post=%s", request.POST)
    result = {"success": False, 'error': 'Could not upload files'}
    if 'qqfile' in request.POST:
        try:
            handle_upload(request, request.POST)
            result = {'success': True}
        except Exception as e:
            msg = "upload failed"
            logger.exception(msg)
            result = {"success": False, 'error': msg}
    return result

@view_defaults(permission='view', layout='default')
class Home(object):
    def __init__(self, request):
        self.request = request
        self.session = self.request.session

    @view_config(route_name='home', renderer='phoenix:templates/home.pt')
    def view(self):
        return {}
