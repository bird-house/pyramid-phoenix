# views.py
# Copyright (C) 2013 the ClimDaPs/Phoenix authors and contributors
# <see AUTHORS file>
#
# This module is part of ClimDaPs/Phoenix and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import os
import datetime

from pyramid.view import view_config, forbidden_view_config
from pyramid.httpexceptions import HTTPException, HTTPFound, HTTPNotFound
from pyramid.response import Response
from pyramid.renderers import render
from pyramid.security import remember, forget, authenticated_userid
from pyramid.events import subscriber, BeforeRender
from pyramid_deform import FormView
from deform import Form
from deform import ValidationFailure
from deform.form import Button
from authomatic import Authomatic
from authomatic.adapters import WebObAdapter
import config_public as config

from owslib.wps import WPSExecution, ComplexData

from .security import is_valid_user
from .models import update_user
from .wps import WPSSchema
from phoenix import catalog

from .helpers import (
    wps_url,
    supervisor_url,
    thredds_url,
    execute_wps
    )

import logging
logger = logging.getLogger(__name__)

authomatic = Authomatic(config=config.config,
                        secret=config.SECRET,
                        report_errors=True,
                        logging_level=logging.DEBUG)

@subscriber(BeforeRender)
def add_global(event):
    event['message_type'] = 'alert-info'
    event['message'] = ''


# Exception view
# --------------

# @view_config(context=Exception)
# def error_view(exc, request):
#     msg = exc.args[0] if exc.args else ''
#     response = Response(str(msg))
#     response.status_int = 500
#     response.content_type = 'text/xml'
#     return response


# sign-in
# -------

@view_config(
    route_name='signin', 
    layout='default', 
    renderer='templates/signin.pt',
    permission='view')
def signin(request):
    logger.debug("sign-in view")
    return dict()

# logout
# --------

@view_config(
    route_name='logout',
    permission='edit')
def logout(request):
    logger.debug("logout")
    headers = forget(request)
    return HTTPFound(location = request.route_url('home'),
                     headers = headers)

# forbidden view
# --------------

@forbidden_view_config(
    renderer='templates/forbidden.pt',
    )
def forbidden(request):
    request.response.status = 403
    return dict(message=None)

# register view
# -------------
@view_config(
    route_name='register',
    renderer='templates/register.pt',
    permission='view')
def register(request):
    return dict(email=None)


# local login for admin and demo user
# -----------------------------------
@view_config(
    route_name='login_local',
    #check_csrf=True, 
    permission='view')
def login_local(request):
    logger.debug("login with local account")
    password = request.params.get('password')
    # TODO: need some work work on local accounts
    if (False):
        email = "demo@climdaps.org"
        update_user(request, user_id=email)

        if is_valid_user(request, email):
            request.response.text = render('phoenix:templates/openid_success.pt',
                                           {'result': email},
                                           request=request)
            # Add the headers required to remember the user to the response
            request.response.headers.extend(remember(request, email))
        else:
            request.response.text = render('phoenix:templates/register.pt',
                                           {'email': email}, request=request)
    else:
        request.response.text = render('phoenix:templates/forbidden.pt',
                                       {'message': 'Wrong Password'},
                                       request=request)

    return request.response

# persona login
# -------------

@view_config(route_name='login', check_csrf=True, renderer='json', permission='view')
def login(request):
    # TODO: update login to my needs
    # https://pyramid_persona.readthedocs.org/en/latest/customization.html#do-extra-work-or-verification-at-login

    logger.debug('login with persona')

    # Verify the assertion and get the email of the user
    from pyramid_persona.views import verify_login 
    email = verify_login(request)

    # update user list
    update_user(request, user_id=email)
    
    # check whitelist
    if not is_valid_user(request, email):
        logger.info("persona login: user %s is not registered", email)
        update_user(request, user_id=email, activated=False)
        #    request.session.flash('Sorry, you are not on the list')
        return {'redirect': '/register', 'success': False}
    logger.info("persona login successful for user %s", email)
    update_user(request, user_id=email, activated=True)
    # Add the headers required to remember the user to the response
    request.response.headers.extend(remember(request, email))
    # Return a json message containing the address or path to redirect to.
    #return {'redirect': request.POST['came_from'], 'success': True}
    return {'redirect': '/', 'success': True}

# authomatic openid login
# -----------------------

@view_config(
    route_name='login_openid',
    permission='view')
def login_openid(request):
    # Get the internal provider name URL variable.
    provider_name = request.matchdict.get('provider_name', 'openid')

    logger.debug('provider_name: %s', provider_name)
    
    # Start the login procedure.
    response = Response()
    #response = request.response
    result = authomatic.login(WebObAdapter(request, response), provider_name)

    #logger.debug('authomatic login result: %s', result)
    
    if result:
        if result.error:
            # Login procedure finished with an error.
            #request.session.flash('Sorry, login failed: %s' % (result.error.message))
            logger.error('openid login failed: %s', result.error.message)
            #response.write(u'<h2>Login failed: {}</h2>'.format(result.error.message))
            response.text = render('phoenix:templates/forbidden.pt',
                                   {'message': result.error.message}, request=request)
        elif result.user:
            # Hooray, we have the user!
            logger.debug("user=%s, id=%s, email=%s",
                      result.user.name, result.user.id, result.user.email)

            if is_valid_user(request, result.user.email):
                logger.info("openid login successful for user %s", result.user.email)
                update_user(request, user_id=result.user.email, openid=result.user.id, activated=True)
                response.text = render('phoenix:templates/openid_success.pt',
                                       {'result': result},
                                       request=request)
                # Add the headers required to remember the user to the response
                response.headers.extend(remember(request, result.user.email))
            else:
                logger.info("openid login: user %s is not registered", result.user.email)
                update_user(request, user_id=result.user.email, openid=result.user.id, activated=False)
                response.text = render('phoenix:templates/register.pt',
                                       {'email': result.user.email}, request=request)
    #logger.debug('response: %s', response)
        
    return response

# home view
# ---------

@view_config(
    route_name='home',
    renderer='templates/home.pt',
    layout='default',
    permission='view'
    )
def home(request):
    lm = request.layout_manager
    lm.layout.add_heading('heading_info')
    lm.layout.add_heading('heading_stats')
    return dict()


# processes
# ---------

def build_processes_form(request, formid='deform'):
    from pyramid.security import has_permission
    from .schema import ProcessSchema
    url = request.session.get('phoenix.wps.url', wps_url(request))
    schema = ProcessSchema().bind(
        wps_url = url,
        allow_admin = has_permission('admin', request.context, request))
    return Form(schema, buttons=('submit',), formid=formid)

def build_processes_wps_form(request, formid='deform'):
    from .schema import SelectWPSSchema
    schema = SelectWPSSchema().bind(
        wps_list = catalog.get_wps_list_as_tuple(request),
        )
    return Form(schema, buttons=('select',), formid=formid)

def eval_processes_form(request, form):
    controls = request.POST.items()
    try:
        captured = form.validate(controls)
        process = captured.get('process', '')
        session = request.session
        session['phoenix.process.identifier'] = process
        session.changed()
    except ValidationFailure as e:
        logger.error('validation of process view failed: message=%s' % (e.message))
    return HTTPFound(location=request.route_url('execute'))

def eval_processes_wps_form(request, form):
    controls = request.POST.items()
    try:
        captured = form.validate(controls)
        url = captured.get('url', '')
        session = request.session
        session['phoenix.wps.url'] = url
        session.changed()
    except ValidationFailure as e:
        logger.error('validation of process view failed: message=%s' % (e.message))
    return HTTPFound(location=request.route_url('processes'))

@view_config(
    route_name='processes',
    renderer='templates/processes.pt',
    layout='default',
    permission='edit'
    )
def processes(request):
    form = build_processes_form(request)
    form_wps = build_processes_wps_form(request)
    if 'submit' in request.POST:
        return eval_processes_form(request, form)
    elif 'select' in request.POST:
        return eval_processes_wps_form(request, form_wps)

    url = wps_url(request)
    session = request.session
    if 'phoenix.wps.url' in session:
        url = session['phoenix.wps.url']
    wps = catalog.get_wps_with_auth(request, url)
    
    appstruct = dict()
    return dict(
        form = form.render(appstruct),
        form_wps = form_wps.render(),
        current_wps = wps, 
        )
   
# jobs
# -------

@view_config(
    route_name='jobs',
    renderer='templates/jobs.pt',
    layout='default',
    permission='edit'
    )
def jobs(request):
    from .models import jobs_information

    jobs = jobs_information(request)

    #This block is used to allow viewing the data if javascript is deactivated
    from pyramid.request import Request
    #create a new request to jobsupdate
    subreq = Request.blank('/jobsupdate/starttime/inverted')
    #copy the cookie for authenication (else 403 error)
    subreq.cookies = request.cookies
    #Make the request
    response = request.invoke_subrequest(subreq)
    #Get the HTML part of the response
    noscriptform = response.body

    if "remove_all" in request.POST:
        from .models import drop_user_jobs
        drop_user_jobs(request)
        
        return HTTPFound(location=request.route_url('jobs'))

    elif "remove_selected" in request.POST:
        if("selected" in request.POST):
            from .models import drop_jobs_by_uuid
            drop_jobs_by_uuid(request,request.POST.getall("selected"))
        return HTTPFound(location=request.route_url('jobs'))

 
    return {"jobs":jobs,"noscriptform":noscriptform}

@view_config(
    route_name="jobsupdate",
    layout='default',
    permission='edit'
    )
def jobsupdate(request):
    from .models import jobs_information
    from .schema import TableSchema
    data = request.matchdict
    #Sort the table with the given key, matching to the template name
    key = data["sortkey"]
    #If inverted is found as type then the ordering is inverted.
    inverted = (data["type"]=="inverted")
    jobs = jobs_information(request,key,inverted)
    #Add HTML data for the table
    def tpd(key,value):
        return (key,{key:"<div id=\""+key+"\" onclick=\"sort(\'"+key+"\')\">"+value+"</div>"})
    table_options = 'id="process_table" class="table table-condensed accordion-group" style="table-layout: fixed; word-wrap: break-word;"'
    tableheader= [tpd('select','Select'),tpd('identifier','Identifier'),
                  tpd('starttime','Start Time'),tpd('duration','Duration'),
                  tpd('notes','Notes'),tpd('tags','Tags'),tpd('status','Status')]
    tablerows = []
    for job in jobs:
        tablerow = []
        job["select"] = '<input type="checkbox" name="selected" value="'+job['uuid']+'">'
        identifier = job["identifier"]
        uuid = job['uuid']
        job["identifier"] ='<a rel="tooltip" data-placement="right" title="ID:'+uuid+'">'+identifier+'</a>'
        for tuplepair in tableheader:
            key = tuplepair[0]
            tablerow.append(job[key])

        status = job["status"]
        tr1 = "Unknown status:"+str(status)
        if status in ["ProcessAccepted","ProcessStarted","ProcessPaused"]:
            perc = job.get("percent_completed")
            barwidth = 80
            barfill = perc*barwidth/100
            tr1 = ('<a href="#" class="label label-info" data-toggle="popover"' +
                       ' data-placement="left" data-content="' + str(job.get("status_message")) +
                       '" data-original-title="Status Message">' + job["status"] + '</a>\n' +
                       '<div><progress style="height:20px;width:' + str(barwidth) + 'px;"  max="' + 
                       str(barwidth) + '" value="' + str(barfill) + '"></progress>' + 
                       str(perc) + '%</div>')
        elif status == "ProcessSucceeded":
            tr1 = (' <a href="/output_details?uuid=' + job["uuid"] + '" class="label label-success">' +
                   status + '</a>')
        elif status == "ProcessFailed":
            tr1 = ('<a href="#" class="label label-warning" data-toggle="popover"' + 
                  ' data-placement="left" data-content="' + job["error_message"] + 
                  '" data-original-title="Error Message">' + status + '</a>')
        elif status == "Exception":
            tr1 = ('<a href="#" class="label label-important" data-toggle="popover"' +
                  ' data-placement="left" data-content="' + job["error_message"] +
                  '" data-original-title="Error Message">'+ status +'</a>')
        #The last element is status
        tablerow[-1] = tr1
        tablerows.append(tablerow)
    #Create a form using the HTML data above and using the TableSchema
    appstruct = {'table':{'tableheader':tableheader, 'tablerows':tablerows,
        'table_options':table_options}}
    schema = TableSchema().bind()
    schema.set_title("My Jobs")
    myForm = Form(schema,buttons=("remove selected","remove all"))
    form = myForm.render(appstruct=appstruct)
    #Change the layout from horizontal to vertical to allow the table take the full width.
    form = form.replace('deform form-horizontal','deform form-vertical')
    return Response(form,content_type='text/html')

# output_details
# --------------

@view_config(
     route_name='output_details',
     renderer='templates/output_details.pt',
     layout='default',
     permission='edit')
def output_details(request):
    title = u"Process Outputs"

    from .models import get_job
    job = get_job(request, uuid=request.params.get('uuid'))
    wps = catalog.get_wps_with_auth(request, job['service_url'])
    execution = WPSExecution(url=wps.url)
    execution.checkStatus(url=job['status_location'], sleepSecs=0)

    form_info="Status: %s" % (execution.status)
    
    return( dict(
        title=execution.process.title, 
        form_info=form_info,
        outputs=execution.processOutputs) )

# form
# -----

@view_config(
    route_name='execute',
    renderer='templates/form.pt',
    layout='default',
    permission='edit'
    )
class ExecuteView(FormView):
    buttons = ('submit',)
    schema_factory = None
    wps = None
   
    def __call__(self):
        # build the schema if it not exist
        if self.schema is None:
            if self.schema_factory is None:
                self.schema_factory = WPSSchema
            
        try:
            session = self.request.session
            identifier = session['phoenix.process.identifier']
            url = wps_url(self.request)
            if 'phoenix.wps.url' in session:
                url = session['phoenix.wps.url']
            self.wps = catalog.get_wps(url)
            process = self.wps.describeprocess(identifier)
            self.schema = self.schema_factory(
                info = True,
                title = process.title,
                process = process)
        except:
            raise
       
        return super(ExecuteView, self).__call__()

    def appstruct(self):
        return None

    def submit_success(self, appstruct):
        session = self.request.session
        identifier = session['phoenix.process.identifier']
        params = self.schema.serialize(appstruct)
      
        execution = execute_wps(self.wps, identifier, params)

        from .models import add_job
        add_job(
            request = self.request, 
            user_id = authenticated_userid(self.request), 
            identifier = identifier, 
            wps_url = self.wps.url, 
            execution = execution,
            notes = params.get('info_notes', ''),
            tags = params.get('info_tags', ''))

        return HTTPFound(location=self.request.route_url('jobs'))

@view_config(
    route_name='monitor',
    renderer='templates/embedded.pt',
    layout='default',
    permission='admin'
    )
def monitor(request):
    return dict(external_url=supervisor_url(request))

@view_config(
    route_name='tds',
    renderer='templates/embedded.pt',
    layout='default',
    permission='edit'
    )
def thredds(request):
    return dict(external_url=thredds_url(request))

def generate_catalog_form(request, formid="deform"):
    """This helper code generates the form that will be used to add
    and edit wps based on the schema of the form.
    """
    from .schema import CatalogSchema
    schema = CatalogSchema().bind()
    options = """
    {success:
       function (rText, sText, xhr, form) {
         deform.processCallbacks();
         deform.focusFirstInput();
         var loc = xhr.getResponseHeader('X-Relocate');
            if (loc) {
              document.location = loc;
            };
         }
    }
    """
    return Form(
        schema,
        buttons=('submit',),
        formid=formid,
        use_ajax=True,
        ajax_options=options,
        )

def process_catalog_form(request, form):
    try:
        controls = request.POST.items()
        captured = form.validate(controls)
        url = captured.get('url', '')
        notes = captured.get('notes', '')
        username = captured.get('username', '')
        password = captured.get('password', '')
        catalog.add_wps_entry(request, url, username, password, notes)
    except ValidationFailure as e:
        logger.error('validation of catalog form failed: message=%s' % (e.message))
    return HTTPFound(location=request.route_url('catalog'))

@view_config(
    route_name="catalog",
    renderer='templates/catalog.pt',
    layout='default',
    permission='edit',
    )
def show_catalog(request):
    form = generate_catalog_form(request)
    if 'submit' in request.POST:
        return process_catalog_form(request, form)
    appstruct = dict(url=wps_url(request))
    return dict(
        wps_list=catalog.get_wps_list(request),
        form = form.render(appstruct))

@view_config(renderer='json', name='delete.entry', permission='edit')
def delete_catalog_entry(context, request):
    """
    Delete a catalog entry, e.a. wps url
    """
    wps_url = request.params.get('url', None)
    logger.debug('delete entry %s' %(wps_url))
    if wps_url is not None:
        catalog.delete_wps_entry(request, wps_url)

    return True

@view_config(renderer='json', name='edit.entry', permission='edit')
def edit_catalog_entry(context, request):
    wps_url = request.params.get('url', None)
    result = dict(url=wps_url)
    logger.debug('delete entry %s' %(wps_url))
    if wps_url is not None:
        entry = catalog.get_wps_entry(request, wps_url)
        result = dict(url=wps_url, notes=entry.get('notes'),
                      username=entry.get('username'),
                      password=entry.get('password'))
    return result

@view_config(
    route_name='admin_user_edit',
    renderer='templates/admin.pt',
    layout='default',
    permission='edit',
    )
class AdminUserEditView(FormView):
    from .schema import AdminUserEditSchema
    
    schema = AdminUserEditSchema()
    buttons = ('edit',)
    title = u"Manage Users"

    def appstruct(self):
        return {}

    def edit_success(self, appstruct):
        params = self.schema.serialize(appstruct)
        user_id = params.get('user_id').pop()

        logger.debug("edit users %s", user_id)

        session = self.request.session
        session['phoenix.admin.edit.user_id'] = user_id
        session.changed()

        return HTTPFound(location=self.request.route_url('admin_user_edit_task'))

@view_config(
    route_name='admin_user_edit_task',
    renderer='templates/admin.pt',
    layout='default',
    permission='edit',
    )
class AdminUserEditTaskView(FormView):
    from .schema import AdminUserEditTaskSchema
    
    schema = AdminUserEditTaskSchema()
    buttons = ('update', 'cancel',)
    title = u"Edit User"

    def appstruct(self):
        from .models import user_with_id
        session = self.request.session
        user_id = session['phoenix.admin.edit.user_id']
        user = user_with_id(self.request, user_id=user_id)
        return dict(
            email = user_id,
            openid = user.get('openid'),
            name = user.get('name'),
            organisation = user.get('organisation'),
            notes = user.get('notes'),
            activated = user.get('activated'),
            )

    def update_success(self, appstruct):
        from .models import update_user
        user = self.schema.serialize(appstruct)
        session = self.request.session
        user_id = session['phoenix.admin.edit.user_id']
        #logger.debug("user activated: %s", user.get('activated') == 'true')
        update_user(self.request,
                      user_id = user_id,
                      openid = user.get('openid'),
                      name = user.get('name'),
                      organisation = user.get('organisation'),
                      notes = user.get('notes'),
                      activated = user.get('activated') == 'true')

        return HTTPFound(location=self.request.route_url('admin_user_edit'))
    
    def cancel_success(self, appstruct):
        return HTTPFound(location=self.request.route_url('admin_user_edit'))


@view_config(
    route_name='admin_user_register',
    renderer='templates/admin.pt',
    layout='default',
    permission='edit',
    )
class AdminUserRegisterView(FormView):
    from .schema import AdminUserRegisterSchema
    
    schema = AdminUserRegisterSchema()
    buttons = ('register',)
    title = u"Register User"

    def appstruct(self):
        return {}

    def register_success(self, appstruct):
        from .models import register_user
        user = self.schema.serialize(appstruct)
        register_user(self.request,
                      user_id = user.get('email'),
                      openid = user.get('openid'),
                      name = user.get('name'),
                      organisation = user.get('organisation'),
                      notes = user.get('notes'),
                      activated = True)

        return HTTPFound(location=self.request.route_url('admin_user_register'))

@view_config(
    route_name='admin_user_unregister',
    renderer='templates/admin.pt',
    layout='default',
    permission='edit',
    )
class AdminUserUnregisterView(FormView):
    from .schema import AdminUserUnregisterSchema
    
    schema = AdminUserUnregisterSchema()
    buttons = ('unregister',)
    title = u"Unregister User"

    def unregister_success(self, appstruct):
        from .models import unregister_user
        params = self.schema.serialize(appstruct)
        for user_id in params.get('user_id', []):
            unregister_user(self.request, user_id=user_id)
        
        return HTTPFound(location=self.request.route_url('admin_user_unregister'))

@view_config(
    route_name='admin_user_activate',
    renderer='templates/admin.pt',
    layout='default',
    permission='edit',
    )
class AdminUserActivateView(FormView):
    from .schema import AdminUserActivateSchema
    
    schema = AdminUserActivateSchema()
    buttons = ('activate',)
    title = u"Activate Users"
    
    def activate_success(self, appstruct):
        from .models import activate_user
        params = self.schema.serialize(appstruct)
        for user_id in params.get('user_id', []):
            activate_user(self.request, user_id=user_id)

        return HTTPFound(location=self.request.route_url('admin_user_activate'))

@view_config(
    route_name='admin_user_deactivate',
    renderer='templates/admin.pt',
    layout='default',
    permission='edit',
    )
class AdminUserDeactivateView(FormView):
    from .schema import AdminUserDeactivateSchema
    
    schema = AdminUserDeactivateSchema()
    buttons = ('deactivate',)
    title = u"Deactivate Users"

    def deactivate_success(self, appstruct):
        from .models import deactivate_user
        params = self.schema.serialize(appstruct)
        for user_id in params.get('user_id', []):
            logger.debug('deactivate user %s', user_id)
            deactivate_user(self.request, user_id=user_id)

        return HTTPFound(location=self.request.route_url('admin_user_deactivate'))

@view_config(
    route_name='map',
    renderer='templates/map.pt',
    layout='default',
    permission='edit'
    )
def map(request):
    # TODO: fix userid with @
    userid=authenticated_userid(request)
    userid = userid.replace('@', '_')
    return dict(userid=userid)

@view_config(
    route_name='help',
    renderer='templates/embedded.pt',
    layout='default',
    permission='view'
    )
def help(request):
    return dict(external_url='/docs')

