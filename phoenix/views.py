import datetime

from pyramid.view import view_config, forbidden_view_config
from pyramid.httpexceptions import HTTPException, HTTPFound, HTTPNotFound
from pyramid.response import Response
from pyramid.security import remember, forget, authenticated_userid
from pyramid.events import subscriber, BeforeRender
from pyramid_deform import FormView
import deform
import peppercorn

from .helpers import get_service_url, mongodb_conn

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

    conn = mongodb_conn(request)
    db = conn.phoenix_db
    for proc in db.history.find(dict(
        user_id=authenticated_userid(request))):
        log.debug(proc)
        log.debug('status_location = %s', proc['status_location'])

        proc['starttime'] = proc['start_time'].strftime('%a, %d %h %Y %I:%M:%S %p')

        if proc['status'] == 'ProcessAccepted':
            wps = WebProcessingService(proc['service_url'], verbose=False)
            execution = WPSExecution(url=wps.url)
            execution.checkStatus(url=proc['status_location'], sleepSecs=0)
            if execution.isComplete():
                proc['status'] = execution.status
            proc['end_time'] = datetime.datetime.now()
           
            # TODO: configure output delete time
            dd = 3
            proc['output_delete_time'] = datetime.datetime.now() + \
                                      datetime.timedelta(days=dd)

        if proc['status'] == 'ProcessAccepted':
            percent = 45  # TODO: poll percent
            proc['progress'] = percent
            proc['duration'] = str(datetime.datetime.now() - proc['start_time'])
        else:
            proc['duration'] = str(proc['end_time'] - proc['start_time'])

        history.append(proc)
        db.history.update({'uuid':proc['uuid']}, proc)

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
        conn = mongodb_conn(request)
        db = conn.phoenix_db
        proc = db.history.find_one({'uuid':request.params.get('uuid')})
        wps = WebProcessingService(proc['service_url'], verbose=False)
        execution = WPSExecution(url=wps.url)
        execution.checkStatus(url=proc['status_location'], sleepSecs=0)
                
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
        for (key, value) in serialized.iteritems():
            inputs.append( (str(key), str(value)) )

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
 
        import uuid
       
        # mongodb
        conn = mongodb_conn(self.request)
        conn.phoenix_db.history.save(dict(
          user_id=authenticated_userid(self.request), 
          uuid=uuid.uuid4().get_hex(),
          identifier=identifier,
          service_url=wps.url,
          status_location=execution.statusLocation,
          status = execution.status,
          user = authenticated_userid(self.request),
          start_time = datetime.datetime.now()
          ))
               
        return HTTPFound(location=self.request.route_url('history'))

@view_config(route_name='monitor',
             renderer='templates/embedded.pt',
             layout='default',
             permission='view'
             )
def monitor(request):
    log.debug('rendering monitor view')
    return dict(external_url='http://localhost:9001')

@view_config(route_name='help',
             renderer='templates/embedded.pt',
             layout='default',
             permission='view'
             )
def help(request):
    log.debug('rendering help view')
    return dict(external_url='/docs')

