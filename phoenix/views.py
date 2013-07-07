import datetime

from pyramid.view import view_config, forbidden_view_config
from pyramid.httpexceptions import HTTPException, HTTPFound, HTTPNotFound
from pyramid.response import Response
from pyramid.security import remember, forget, authenticated_userid
from pyramid.events import subscriber, BeforeRender
from pyramid_deform import FormView
import deform
import peppercorn

from .models import DBSession, ProcessHistory, Status
from .helpers import get_service_url

import logging

log = logging.getLogger(__name__)

from owslib.wps import WebProcessingService, WPSExecution

@subscriber(BeforeRender)
def add_global(event):
    event['message_type'] = 'alert-info'
    event['message'] = ''

#==============================================================================
# Exception view
#==============================================================================

# @view_config(context=Exception)
# def error_view(exc, request):
#     msg = exc.args[0] if exc.args else ''
#     response = Response(str(msg))
#     response.status_int = 500
#     response.content_type = 'text/xml'
#     return response


#==============================================================================
# home
#==============================================================================

@view_config(route_name='home',
             renderer='templates/home.pt',
             layout='default',
             permission='view'
             )
def home(request):
    log.debug('rendering home view')

    lm = request.layout_manager
    lm.layout.add_heading('heading_processes')
    lm.layout.add_heading('heading_history')
    return dict()


#==============================================================================
# processes
#==============================================================================


@view_config(route_name='processes',
             renderer='templates/processes.pt',
             layout='default',
             permission='view'
             )
def processes(request):
    wps = WebProcessingService(get_service_url(request), verbose=False, skip_caps=True)
    wps.getcapabilities()
    return dict( wps=wps, logged_in=authenticated_userid(request))
   
#==============================================================================
# history
#==============================================================================

@view_config(route_name='history',
             renderer='templates/history.pt',
             layout='default',
             permission='edit'
             )
def history(request):
    log.debug('rendering history')

    history = []

    for proc in ProcessHistory.by_userid(authenticated_userid(request)):
        h = dict(uuid=proc.uuid, 
                 identifier=proc.identifier,
                 status_location=proc.status_location)

        log.debug('status_location = %s', proc.status_location)

        h['starttime'] = proc.start_time.strftime('%a, %d %h %Y %I:%M:%S %p')

        if proc.status.id == 1:
            wps = WebProcessingService(proc.service_url, verbose=False, skip_caps=True)
            execution = WPSExecution(url=wps.url)
            execution.checkStatus(url=h['status_location'], sleepSecs=0)
            if execution.isComplete():
                if execution.isSucceded():
                    proc.status = Status.by_id(2)
                else:
                    proc.status = Status.by_id(4)
                    proc.run_message = execution.status

            proc.end_time = datetime.datetime.now()

            # TODO: configure output delete time
            dd = 3
            proc.output_delete_time = datetime.datetime.now() + \
                                      datetime.timedelta(days=dd)

        if proc.status.id == 1:
            percent = 45  # TODO: poll percent
            h['status'] = (1, proc.status.status, percent)

            h['duration'] = str(datetime.datetime.now() - proc.start_time)
        else:
            h['duration'] = str(proc.end_time - proc.start_time)

            if proc.status.id == 2:
                h['status'] = (2, proc.status.status, 'success')
            elif proc.status.id == 3:
                h['status'] = (3, proc.status.status, 'warning')
            elif proc.status.id == 4:
                h['status'] = (4, proc.status.status, 'important', proc.run_message)

        history.append(h)

        log.debug('leaving history')

    return dict(history=history)


#==============================================================================
# output_details
#==============================================================================

@view_config(
             route_name='output_details',
             renderer='templates/form.pt',
             layout='default',
             permission='edit'
             )
def output_details(request):
    log.debug('rendering output_details')
    from .schema import OutputDetails
    schema = OutputDetails()
    myform = deform.Form(schema)

    appstruct = {
               
                'result' : 'nothing',
                'complete' : False,
                'succeded' : False,
            }
    if 'uuid' in request.params:
        proc = ProcessHistory.by_uuid(request.params.get('uuid'))
        wps = WebProcessingService(proc.service_url, verbose=False)
        execution = WPSExecution(url=wps.url)
        execution.checkStatus(url=proc.status_location, sleepSecs=0)
                
        appstruct = {
           
            'identifier' : execution.process.identifier,
            'complete' : execution.isComplete(),
            'succeded' : execution.isSucceded(),
            'contents'  : []  
        }
        for output in execution.processOutputs:
            if output.reference is not None:
                content = {'data' : output.reference, 'reference' : True}
                appstruct['contents'].append(content)
            else:
                content = {'data' : output.data, 'reference' : False}
                appstruct['contents'].append(content)
    log.debug('out appstruct = %s', appstruct)

    form = myform.render(appstruct, readonly=True)
    return dict(form=form)



#==============================================================================
# login
#==============================================================================

# @view_config(route_name='login',
#              renderer='templates/login.pt',
#              layout='default')
# @forbidden_view_config(renderer='templates/login.pt')
# def login(request):
#     login_url = request.route_url('login')
#     referrer = request.url

#     if referrer == login_url:
#         referrer = '/'  # never use the login form itself as came_from

#     came_from = request.params.get('came_from', referrer)
#     message_type = 'alert-error'
#     message = ''
#     login = ''
#     password = ''

#     if 'form.submitted' in request.params:
#         login = request.params['login'].lower().strip()
#         password = request.params['password']

#         user = User.by_name(login)

#         if user and user.validate_password(password):
#             if user.disabled:
#                 message = 'Your profile is disabled. ' \
#                           'Please contact support for assistance.'
#             else:
#                 headers = remember(request, user.id)

#                 if user.lastlogin is None and user.id == 1:
#                     return HTTPFound(location=request.route_url('profile'),
#                                      headers=headers)
#                 else:
#                     response = HTTPFound(location=came_from, headers=headers)
#                     if user.lastlogin is not None:
#                         response.set_cookie('lastlogin',
#                                             user.lastlogin.strftime(
#                                                    '%a, %d %h %Y %I:%M:%S %p'))
#                     user.lastlogin = datetime.datetime.now()
#                     return response
#         else:
#             message = 'Incorrect Username or Password!'

#     return dict(url=login_url, came_from=came_from, login=login,
#                 password=password, message_type=message_type, message=message)




#==============================================================================
# logout
#==============================================================================

# @view_config(route_name='logout',
#              layout='default')
# def logout(request):
#     headers = forget(request)
#     response = HTTPFound(location=request.route_url('home'), headers=headers)
#     response.delete_cookie('lastlogin')
#     return response


#==============================================================================
# form
#==============================================================================

@view_config(route_name='form',
             renderer='templates/form.pt',
             layout='default',
             permission='view'
             )
class ExecuteView(FormView):
    log.debug('rendering execute')
    #form_info = "Hover your mouse over the widgets for description."
    buttons = ('submit',)
    title = u"Process Output"
    schema_factory = None
   
    def __call__(self):
        from .schema import DataInputsSchema  
        
        # build the schema if it not exist
        if self.schema is None:
            if self.schema_factory is None:
                self.schema_factory = DataInputsSchema
            self.schema = self.schema_factory()

        try:
            identifier = self.request.params.get('identifier')
            wps = WebProcessingService(get_service_url(self.request), verbose=False)
            process = wps.describeprocess(identifier)
            DataInputsSchema.build(schema=self.schema, process=process)
        except:
            raise
       
        return super(ExecuteView, self).__call__()

    def appstruct(self):
        return {}

    def submit_success(self, appstruct):
        log.debug('execute process')
        log.debug('appstruct = %s', appstruct)
        from owslib.wps import monitorExecution

        identifier = self.request.params.get("identifier")
        log.debug('identifier = %s', identifier)
        # params = peppercorn.parse(request.params.items())

        # if 'gui_desc' in params:
        #     inputs = {'literal': {}, 'complex': {}, 'boundingbox': {}}

        #     for k, v in eval(params['gui_desc']).items():
        #         if v.startswith('literal'):
        #             inputs['literal'][k] = params[k]
        #         elif v.startswith('complex'):
        #             if v.split(':')[1] == 'list':
        #                 inputs['complex'][k] = params[k].split()
        #             else:
        #                 inputs['complex'][k] = [params[k]]
        #         elif v.startswith('boundingbox'):
        #             inputs['boundingbox'][k] = params[k]

        inputs = []
        serialized = self.schema.serialize(appstruct)
        for item in serialized.iteritems():
            inputs.append( item )

        log.debug('inputs =  %s', inputs)

        wps = WebProcessingService(get_service_url(self.request), verbose=False)
        process = wps.describeprocess(identifier)

        outputs = []
        for output in process.processOutputs:
            outputs.append( (output.identifier, output.dataType == 'ComplexData' ) )

        log.debug('before wps.execute')
        execution = wps.execute(identifier, inputs=inputs, output=outputs)
        #execution = wps.execute(identifier, inputs, output="out")
        log.debug('after wps.execute')

        # TODO: handle sync/async case, 
        # TODO: fix wps-client (parsing response)
        # TODO: fix wps-client for store/status setting or use own xml template
        
        log.debug('status_location = %s', execution.statusLocation)

        session = DBSession()
        import uuid
        proc = ProcessHistory(
            #TODO set uuid of pywps
                       user_id=authenticated_userid(self.request), 
                       uuid=uuid.uuid4().get_hex(),
                       identifier=identifier,
                       service_url=wps.url,
                       status_location=execution.statusLocation)
        proc.status = Status.by_id(1)
        proc.user = authenticated_userid(self.request)
        proc.start_time = datetime.datetime.now()
               
        return HTTPFound(location=self.request.route_url('history'))
