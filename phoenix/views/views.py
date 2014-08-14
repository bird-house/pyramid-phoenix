import os
import datetime

from pyramid.view import (
    view_config,
    view_defaults,
    forbidden_view_config,
    notfound_view_config
    )
from pyramid.httpexceptions import HTTPException, HTTPFound, HTTPNotFound
from pyramid.response import Response
from pyramid.renderers import render
from pyramid.security import remember, forget, authenticated_userid
from pyramid.events import subscriber, BeforeRender
from deform import Form, Button
from deform import ValidationFailure
from authomatic import Authomatic
from authomatic.adapters import WebObAdapter

from owslib.wps import (
    WebProcessingService,
    WPSExecution,
    )

from phoenix import models

import logging
logger = logging.getLogger(__name__)

from phoenix import config_public as config
authomatic = Authomatic(config=config.config,
                        secret=config.SECRET,
                        report_errors=True,
                        logging_level=logging.DEBUG)

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

class MyView(object):
    def __init__(self, request, title, description=None):
        self.request = request
        self.session = self.request.session
        self.title = title
        self.description = description
        # db access
        self.userdb = self.request.db.users

    def user_email(self):
        return authenticated_userid(self.request)

    def get_user(self, email=None):
        if email is None:
            email = self.user_email()
        return self.userdb.find_one(dict(email=email))

@view_defaults(permission='view', layout='default')
class PhoenixView(MyView):
    def __init__(self, request):
        super(PhoenixView, self).__init__(request, 'Phoenix')

    def is_valid_user(self, email):
        from .security import admin_users
        if email in admin_users(self.request):
            return True
        user = self.get_user(email=email)
        if user is None:
            return False
        return user.get('activated', False)

    def login_success(self, email, openid=None, activated=False):
        logger.debug('login success: email=%s', email)
        user = self.get_user(email)
        if user is None:
            user = models.add_user(self.request, email=email)
        user['last_login'] = datetime.datetime.now()
        if openid is not None:
            user['openid'] = openid
        user['activated'] = activated
        logger.debug('user=%s', user)
        self.userdb.update({'email':email}, user)

    @view_config(route_name='dummy', renderer='phoenix:templates/dummy.pt')
    @view_config(route_name='dummy_json', renderer='json')
    def dummy(self):
        email = self.request.matchdict['email']
        now = datetime.datetime.now()
        return dict(name="dummy", email=email, now=now)

    @view_config(route_name='signin', renderer='phoenix:templates/signin.pt')
    def signin(self):
        return dict()

    @view_config(route_name='logout', permission='edit')
    def logout(self):
        headers = forget(self.request)
        return HTTPFound(location = self.request.route_url('home'), headers = headers)

    @view_config(route_name='register', renderer='phoenix:templates/register.pt')
    def register(self):
        return dict(email=None)

    @view_config(route_name='login_local')
    def login_local(self):
        """local login for admin and demo user"""
        
        # TODO: need some work work on local accounts
        if (True):
            email = "admin@malleefowl.org"
            if self.is_valid_user(email):
                self.request.response.text = render('phoenix:templates/openid_success.pt',
                                               {'result': email},
                                               request=self.request)
                # Add the headers required to remember the user to the response
                self.request.response.headers.extend(remember(self.request, email))
                self.login_success(email=email)
            else:
                self.request.response.text = render('phoenix:templates/register.pt',
                                               {'email': email}, request=self.request)
        else:
            self.request.response.text = render('phoenix:templates/forbidden.pt',
                                           {'message': 'Wrong Password'},
                                           request=self.request)

        return self.request.response

    @view_config(route_name='login_openid')
    def login_openid(self):
        """authomatic openid login"""
        # Get the internal provider name URL variable.
        provider_name = self.request.matchdict.get('provider_name', 'openid')

        logger.debug('provider_name: %s', provider_name)

        # Start the login procedure.
        response = Response()
        #response = request.response
        result = authomatic.login(WebObAdapter(self.request, response), provider_name)

        logger.debug('authomatic login result: %s', result)

        if result:
            if result.error:
                # Login procedure finished with an error.
                #request.session.flash('Sorry, login failed: %s' % (result.error.message))
                logger.error('openid login failed: %s', result.error.message)
                #response.write(u'<h2>Login failed: {}</h2>'.format(result.error.message))
                response.text = render('phoenix:templates/forbidden.pt',
                                       {'message': result.error.message}, request=self.request)
            elif result.user:
                # Hooray, we have the user!
                logger.debug("user=%s, id=%s, email=%s, credentials=%s",
                          result.user.name, result.user.id, result.user.email, result.user.credentials)
                logger.debug("provider=%s", result.provider.name )
                logger.debug("response headers=%s", response.headers.keys())
                #logger.debug("response cookie=%s", response.headers['Set-Cookie'])

                if self.is_valid_user(result.user.email):
                    logger.info("openid login successful for user %s", result.user.email)
                    self.login_success(
                        email=result.user.email,
                        openid=result.user.id,
                        activated=True)
                    response.text = render('phoenix:templates/openid_success.pt',
                                           {'result': result},
                                           request=self.request)
                    # Add the headers required to remember the user to the response
                    response.headers.extend(remember(self.request, result.user.email))
                else:
                    logger.info("openid login: user %s is not registered", result.user.email)
                    self.login_success(
                        email=result.user.email,
                        openid=result.user.id,
                        activated=False)
                    response.text = render('phoenix:templates/register.pt',
                                           {'email': result.user.email}, request=self.request)
        #logger.debug('response: %s', response)

        return response

    @view_config(route_name='home', renderer='phoenix:templates/home.pt')
    def home(self):
        #lm = self.request.layout_manager
        #lm.layout.add_heading('info')
        return dict()

@view_defaults(permission='edit', layout='default')
class ProcessList(MyView):
    def __init__(self, request):
        super(ProcessList, self).__init__(request, 'Processes')

        self.wps = None
        if 'wps.url' in self.session:
            try:
                self.wps = WebProcessingService(url=self.session['wps.url'])
                self.description = self.wps.identification.title
            except:
                msg = "Could not connect to wps"
                logger.exception(msg)
                self.session.flash(msg, queue='error')

    def sort_order(self):
        """Determine what the current sort parameters are.
        """
        order = self.request.GET.get('order_col', 'identifier')
        order_dir = self.request.GET.get('order_dir', 'asc')
        ## if order == 'due_date':
        ##     # handle sorting of NULL values so they are always at the end
        ##     order = 'CASE WHEN due_date IS NULL THEN 1 ELSE 0 END, due_date'
        ## if order == 'task':
        ##     # Sort ignoring case
        ##     order += ' COLLATE NOCASE'
        order_dir = 1 if order_dir == 'asc' else -1
        return dict(order=order, order_dir=order_dir)
    
    def generate_form(self, formid='deform'):
        from phoenix.schema import ChooseWPSSchema
        schema = ChooseWPSSchema().bind(wps_list = models.get_wps_list(self.request))
        return Form(
            schema,
            buttons=('submit',),
            formid=formid
            )
    def process_form(self, form):
        controls = self.request.POST.items()
        try:
            captured = form.validate(controls)
            url = captured.get('url', '')
            session = self.request.session
            session['wps.url'] = url
            session.changed()
        except ValidationFailure, e:
            logger.exception('validation of process view failed.')
            return dict(form=e.render())
        return HTTPFound(location=self.request.route_url('process_list'))

    @view_config(route_name='process_list', renderer='phoenix:templates/process_list.pt')
    def view(self):
        form = self.generate_form()
        if 'submit' in self.request.POST:
            return self.process_form(form)

        items = []
        if self.wps is not None:
            for process in self.wps.processes:
                # TODO: sometime no abstract avail. Fix handling this in owslib
                abstract = ''
                if hasattr(process, 'abstract'):
                    abstract = process.abstract
                processVersion = ''
                if hasattr(process, 'processVersion'):
                    processVersion = process.processVersion
                items.append(dict(title=process.title,
                                  identifier=process.identifier,
                                  abstract=abstract,
                                  version=processVersion))

        # sort items
        order = self.sort_order()
        import operator
        items.sort(key=operator.itemgetter(order['order']), reverse=order['order_dir']==-1)

        from phoenix.grid import ProcessesGrid
        grid = ProcessesGrid(
                self.request,
                items,
                ['title', 'abstract', 'action'],
            )
        return dict(
            grid=grid,
            items=items,
            form=form.render())

@view_defaults(permission='edit', layout='default')
class ExecuteProcess(MyView):
    def __init__(self, request):
        super(ExecuteProcess, self).__init__(request, 'Execute')
        self.top_title = "Processes"
        self.top_route_name = "process_list"

        self.db = self.request.db
       
        self.identifier = self.request.params.get('identifier', None)
        self.wps = self.request.wps
        if 'wps.url' in self.session:
            url = self.session['wps.url']
            self.wps = WebProcessingService(url)
        self.process = self.wps.describeprocess(self.identifier)
        self.description = self.process.title

    def generate_form(self, formid='deform'):
        from .wps import WPSSchema
        # TODO: should be WPSSchema.bind() ...
        schema = WPSSchema(info=True, process = self.process)
        return Form(
            schema,
            buttons=('submit',),
            formid=formid,
            )
    
    def process_form(self, form):
        controls = self.request.POST.items()
        try:
            appstruct = form.validate(controls)

            from .helpers import execute_wps
            execution = execute_wps(self.wps, self.identifier, appstruct)

            models.add_job(
                request = self.request,
                title = execution.process.title,
                wps_url = execution.serviceInstance,
                status_location = execution.statusLocation,
                notes = appstruct.get('info_notes', ''),
                tags = appstruct.get('info_tags', ''))
        except ValidationFailure, e:
            logger.exception('validation of exectue view failed.')
            return dict(form = e.render())
        return HTTPFound(location=self.request.route_url('myjobs'))

    @view_config(route_name='execute_process', renderer='phoenix:templates/execute_process.pt')
    def execute_view(self):
        form = self.generate_form()
        if 'submit' in self.request.POST:
            return self.process_form(form)
        return dict(form=form.render())
    
