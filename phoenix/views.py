import datetime
import types

from pyramid.view import view_config, forbidden_view_config
from pyramid.httpexceptions import HTTPException, HTTPFound, HTTPNotFound
from pyramid.response import Response
from pyramid.security import remember, forget, authenticated_userid
from pyramid.events import subscriber, BeforeRender
from pyramid_deform import FormView, FormWizard, FormWizardView
from pyramid_persona.views import verify_login 
import deform
import peppercorn

from .helpers import wps_url, update_wps_url, csw_url, esgsearch_url, whitelist, mongodb_conn, is_url
from .helpers import esgf_search_context

import logging

log = logging.getLogger(__name__)

from owslib.csw import CatalogueServiceWeb
from owslib.wps import WebProcessingService, WPSExecution, ComplexData

__tagstruct__ = {}

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


# login
# -----

@view_config(route_name='login', check_csrf=True, renderer='json')
def login(request):
    # TODO: update login to my needs
    # https://pyramid_persona.readthedocs.org/en/latest/customization.html#do-extra-work-or-verification-at-login

    # Verify the assertion and get the email of the user
    email = verify_login(request)
    # check whitelist
    if email not in whitelist(request):
        request.session.flash('Sorry, you are not on the list')
        return {'redirect': '/', 'success': False}
    # Add the headers required to remember the user to the response
    request.response.headers.extend(remember(request, email))
    # Return a json message containing the address or path to redirect to.
    return {'redirect': request.POST['came_from'], 'success': True}

# logout
# ------


@view_config(route_name='logout', check_csrf=True, renderer='json')
def logout(request):
    request.response.headers.extend(forget(request))
    return {'redirect': request.POST['came_from']}


# home view
# ---------

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


# processes
# ---------

@view_config(route_name='processes',
             renderer='templates/processes.pt',
             layout='default',
             permission='view'
             )
def processes(request):
    wps = WebProcessingService(wps_url(request), verbose=False, skip_caps=True)
    wps.getcapabilities()
    return dict( wps=wps, logged_in=authenticated_userid(request))
   
# history
# -------

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

        # TODO: handle different process status
        if proc['status'] in ['ProcessAccepted', 'ProcessStarted', 'ProcessPaused']:
            proc['errors'] = []
            try:
                wps = WebProcessingService(proc['service_url'], verbose=False)
                execution = WPSExecution(url=wps.url)
                execution.checkStatus(url=proc['status_location'], sleepSecs=0)
                proc['status'] = execution.status
                proc['percent_completed'] = execution.percentCompleted
                proc['status_message'] = execution.statusMessage
                proc['error_message'] = ''
                for err in execution.errors:
                    proc['errors'].append( dict(code=err.code, locator=err.locator, text=err.text) )
               
            except:
                msg = 'could not access wps %s' % (proc['status_location'])
                log.warn(msg)
                proc['status'] = 'Exception'
                proc['errors'].append( dict(code='', locator='', text=msg) )
            
            proc['end_time'] = datetime.datetime.now()
            for err in proc['errors']:
                proc['error_message'] = err.get('text', '') + ';'

            # TODO: configure output delete time
            dd = 3
            proc['output_delete_time'] = datetime.datetime.now() + datetime.timedelta(days=dd)
            percent = 45  # TODO: poll percent
            proc['duration'] = str(proc['end_time'] - proc['start_time'])
            db.history.update({'uuid':proc['uuid']}, proc)
        history.append(proc)
        
        log.debug('leaving history')

    return dict(history=history)

# output_details
# --------------

class ReadOnlyView(FormView):
    def show(self, form):
        appstruct = self.appstruct()
        if appstruct is None:
            rendered = form.render(readonly=True)
        else:
            rendered = form.render(appstruct, readonly=True)
        return { 'form': rendered, }

@view_config(
     route_name='output_details',
     renderer='templates/form.pt',
     layout='default',
     permission='edit')
class ProcessOutputsView(ReadOnlyView):
    log.debug('output details execute')
    title = u"Process Outputs"
    from .schema import output_schema
    schema = output_schema()
   
    def appstruct(self):
        conn = mongodb_conn(self.request)
        db = conn.phoenix_db
        proc = db.history.find_one({'uuid':self.request.params.get('uuid')})
        self.wps = WebProcessingService(proc['service_url'], verbose=False)
        self.execution = WPSExecution(url=self.wps.url)
        self.execution.checkStatus(url=proc['status_location'], sleepSecs=0)

        appstruct = {
            'identifier' : self.execution.process.identifier,
            'complete' : self.execution.isComplete(),
            'succeded' : self.execution.isSucceded(),
        }

        appstruct['outputs'] = []
        for output in self.execution.processOutputs:
            output_appstruct = {}
            output_appstruct['name'] = output.title
            output_appstruct['mime_type'] = output.mimeType
            output_appstruct['data_type'] = output.dataType
            if output.reference != None:
                output_appstruct['reference'] = output.reference
            output_appstruct['data'] = []
            for datum in output.data:
                data_appstruct = {}
                if isinstance(datum, ComplexData):
                    data_appstruct['reference'] = datum.readonly
                    data_appstruct['mime_type'] = datum.mimeType
                else:
                    data_appstruct['value'] = datum
                output_appstruct['data'].append(data_appstruct)
            appstruct['outputs'].append(output_appstruct)
          
        log.debug('out appstruct = %s', appstruct)

        return appstruct

# form
# -----

@view_config(route_name='form',
             renderer='templates/form.pt',
             layout='default',
             permission='edit'
             )
class ExecuteView(FormView):
    log.debug('rendering execute')
    #form_info = "Hover your mouse over the widgets for description."
    buttons = ('submit',)
    title = u"Process Output"
    schema_factory = None
    wps = None
    process = None
    input_types = None
   
    def __call__(self):
        from .schema import DataInputsSchema  
        
        # build the schema if it not exist
        if self.schema is None:
            if self.schema_factory is None:
                self.schema_factory = DataInputsSchema
            self.schema = self.schema_factory()

        try:
            identifier = self.request.params.get('identifier')
            self.wps = WebProcessingService(wps_url(self.request), verbose=True)
            self.process = self.wps.describeprocess(identifier)
            DataInputsSchema.build(schema=self.schema, process=self.process)

            self.input_types = {}
            for data_input in self.process.dataInputs:
                self.input_types[data_input.identifier] = data_input.dataType
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

        inputs = []
        serialized = self.schema.serialize(appstruct)
        # TODO: dont append value if default
        for (key, value) in serialized.iteritems():
            values = []
            # TODO: how do i handle serveral values in wps?
            if type(value) == types.ListType:
                values = value
            else:
                values = [value]

            # there might be more than one value (maxOccurs > 1)
            for value in values:
                # bbox
                if self.input_types[key] == None:
                    # TODO: handle bounding box
                    log.debug('bbox value: %s' % value)
                    inputs.append( (key, str(value)) )
                    # if len(value) > 0:
                    #     (minx, miny, maxx, maxy) = value[0].split(',')
                    #     bbox = [[float(minx),float(miny)],[float(maxx),float(maxy)]]
                    #     inputs.append( (key, str(bbox)) )
                    # else:
                    #     inputs.append( (key, str(value)) )
                # complex data
                elif self.input_types[key] == 'ComplexData':
                    # TODO: handle complex data
                    log.debug('complex value: %s' % value)
                    if is_url(value):
                        inputs.append( (key, value) )
                    elif type(value) == type({}):
                        if value.has_key('fp'):
                            str_value = value.get('fp').read()
                            inputs.append( (key, str_value) )
                    else:
                        inputs.append( (key, str(value) ))
                else:
                    inputs.append( (key, str(value)) )

        log.debug('inputs =  %s', inputs)

        outputs = []
        for output in self.process.processOutputs:
            outputs.append( (output.identifier, output.dataType == 'ComplexData' ) )

        log.debug('before wps.execute')
        execution = self.wps.execute(identifier, inputs=inputs, output=outputs)
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
          service_url=self.wps.url,
          status_location=execution.statusLocation,
          status = execution.status,
          user = authenticated_userid(self.request),
          start_time = datetime.datetime.now(),
          end_time = datetime.datetime.now(),
          ))
               
        return HTTPFound(location=self.request.route_url('history'))

@view_config(route_name='monitor',
             renderer='templates/embedded.pt',
             layout='default',
             permission='edit'
             )
def monitor(request):
    log.debug('rendering monitor view')
    return dict(external_url='http://localhost:9001')


@view_config(route_name='catalog_wps_add',
             renderer='templates/catalog.pt',
             layout='default',
             permission='edit',
             )
class CatalogAddWPSView(FormView):
    #form_info = "Hover your mouse over the widgets for description."
    schema = None
    schema_factory = None
    buttons = ('add',)
    title = u"Catalog"

    def __call__(self):
        csw = CatalogueServiceWeb(csw_url(self.request))
        csw.getrecords2(maxrecords=100)
        wps_list = []
        for rec_id in csw.records:
            rec = csw.records[rec_id]
            if rec.format == 'WPS':
                wps_list.append((rec.references[0]['url'], rec.title))

        from .schema import CatalogAddWPSSchema
        # build the schema if it not exist
        if self.schema is None:
            if self.schema_factory is None:
                self.schema_factory = CatalogAddWPSSchema
            self.schema = self.schema_factory().bind(
                wps_list = wps_list,
                readonly = True)

        return super(CatalogAddWPSView, self).__call__()

    def appstruct(self):
        return {'current_wps' : wps_url(self.request)}

    def add_success(self, appstruct):
        serialized = self.schema.serialize(appstruct)
        url = serialized['wps_url']

        csw = CatalogueServiceWeb(csw_url(self.request))
        csw.harvest(url, 'http://www.opengis.net/wps/1.0.0')

        return HTTPFound(location=self.request.route_url('catalog_wps_add'))

@view_config(route_name='catalog_wps_select',
             renderer='templates/catalog.pt',
             layout='default',
             permission='edit',
             )
class CatalogSelectWPSView(FormView):
    log.debug('rendering catalog select wps')
    #form_info = "Hover your mouse over the widgets for description."
    schema = None
    schema_factory = None
    buttons = ('submit',)
    title = u"Catalog"

    def __call__(self):
        csw = CatalogueServiceWeb(csw_url(self.request))
        csw.getrecords2(maxrecords=100)
        wps_list = []
        for rec_id in csw.records:
            rec = csw.records[rec_id]
            if rec.format == 'WPS':
                wps_list.append((rec.references[0]['url'], rec.title))

        from .schema import CatalogSelectWPSSchema
        # build the schema if it not exist
        if self.schema is None:
            if self.schema_factory is None:
                self.schema_factory = CatalogSelectWPSSchema
            self.schema = self.schema_factory().bind(wps_list = wps_list)

        return super(CatalogSelectWPSView, self).__call__()

    def appstruct(self):
        return {'active_wps' : wps_url(self.request)}

    def submit_success(self, appstruct):
        serialized = self.schema.serialize(appstruct)
        wps_id = serialized['active_wps']
        log.debug('wps_id = %s', wps_id)
        update_wps_url(self.request, wps_id)        

        return HTTPFound(location=self.request.route_url('catalog_wps_select'))

@view_config(route_name='admin',
             renderer='templates/form.pt',
             layout='default',
             permission='edit',
             )
class AdminView(FormView):
    from .schema import AdminSchema

    log.debug('rendering admin view')
    #form_info = "Hover your mouse over the widgets for description."
    schema = AdminSchema()
    buttons = ('clear_database',)
    title = u"Administration"

    def appstruct(self):
        # mongodb
        conn = mongodb_conn(self.request)
        db = conn.phoenix_db
               
        return {'history_count' : db.history.count()}

    def clear_database_success(self, appstruct):
        # mongodb
        conn = mongodb_conn(self.request)
        conn.phoenix_db.history.drop()
        conn.phoenix_db.search.drop()
               
        return HTTPFound(location=self.request.route_url('admin'))

from pyesgf.search import SearchConnection

@view_config(route_name='search',
             renderer='templates/form.pt',
             layout='default',
             permission='edit',
             )
class SearchView(FormView):
    log.debug('rendering search view')
    #form_info = "Hover your mouse over the widgets for description."
    schema = None
    schema_factory = None
    buttons = ('update', 'tag', 'download',)
    title = u"Search"

    search_conn = None
    search_context = None

    def __call__(self):
        from .schema import SearchSchema
        # build the schema
        if self.schema_factory is None:
            self.schema_factory = SearchSchema
            self.search_conn = SearchConnection(esgsearch_url(self.request), distrib=False)
            self.search_context = self.search_conn.new_context(
                project='CMIP5', product='output1', 
                replica=False, latest=True)
        tags = {}
        db_conn = mongodb_conn(self.request)
        entry =db_conn.phoenix_db.search.find_one({'id':1})
        if entry == None:
            db_conn.phoenix_db.search.save(dict(id=1, tags=tags))
        else:
            tags = entry.get('tags', {})
        self.search_context = self.search_context.constrain(**tags)
        self.schema = self.schema_factory().bind(
            tags = tags,
            search_context = self.search_context)

        return super(SearchView, self).__call__()

    def appstruct(self):
        return {'hit_count' : self.search_context.hit_count}
       
    def update_success(self, appstruct):
        return HTTPFound(location=self.request.route_url('search'))

    def tag_success(self, appstruct):
        facet = appstruct['facet']
        item = appstruct['item']
       
        tags = {}
        db_conn = mongodb_conn(self.request)
        entry = db_conn.phoenix_db.search.find_one({'id':1})
        tags = entry.get('tags', {})
        tags[facet] = item
        log.debug('tags = %s' % (tags))
        db_conn.phoenix_db.search.update(dict(id=1), dict(id=1, tags=tags))
        return HTTPFound(location=self.request.route_url('search'))

    def download_success(self, appstruct):
        opendap_url = appstruct['opendap_url']

class WorkflowFormWizard(FormWizard):
    def __init__(self, name, done, *schemas):
        log.debug('init wizard')
        FormWizard.__init__(self, name, done, *schemas)

    def __call__(self, request):
        FormWizard.__call__(self, request)

class WorkflowFormView(FormView):
    pass
         
class WorkflowFormWizardView(FormWizardView):
    form_view_class = WorkflowFormView

    def __init__(self, wizard):
        log.debug('init esgf search')
        FormWizardView.__init__(self, wizard)

    def __call__(self, request):
        global __tagstruct__

        self.request = request
        self.search_context = esgf_search_context(request)
        self.wizard_state = self.wizard_state_class(request, self.wizard.name)
        step = self.wizard_state.get_step_num()
        
        if step > len(self.wizard.schemas)-1:
            states = self.wizard_state.get_step_states()
            result = self.wizard.done(request, states)
            self.wizard_state.clear()
            return result
        form_view = self.form_view_class(request)
        schema = self.wizard.schemas[step]
        state = self.wizard_state.get_step_state(None)
        state = self.deserialize(state)
        self.search_context = self.search_context.constrain(**__tagstruct__)
        self.schema = schema.bind(
            request=request, 
            search_context=self.search_context,
            tagstruct=__tagstruct__,
            state=state)
        form_view.schema = self.schema
        buttons = []

        prev_disabled = False
        next_disabled = False
        update_disabled = True
        tag_disabled = True

        if hasattr(schema, 'prev_ok'):
            prev_disabled = not schema.prev_ok(request)

        if hasattr(schema, 'next_ok'):
            next_disabled = not schema.next_ok(request)
            
        if hasattr(schema, 'update_ok'):
            update_disabled = not schema.update_ok(request)

        if hasattr(schema, 'tag_ok'):
            tag_disabled = not schema.tag_ok(request)

        prev_button = deform.form.Button(name='previous', title='Previous',
                                         disabled=prev_disabled)
        next_button = deform.form.Button(name='next', title='Next',
                             disabled=next_disabled)
        done_button = deform.form.Button(name='next', title='Done',
                             disabled=next_disabled)
        update_button = deform.form.Button(name='update', title='Update',
                               disabled=update_disabled)
        tag_button = deform.form.Button(name='tag', title='Tag',
                                        disabled=tag_disabled)

        if step > 0:
            buttons.append(prev_button)
        else:
            __tagstruct__ = {}

        if step < len(self.wizard.schemas)-1:
            buttons.append(next_button)
        else:
            buttons.append(done_button)

        if not update_disabled:
            buttons.append(update_button)

        if not tag_disabled:
            buttons.append(tag_button)

        form_view.buttons = buttons
        form_view.next_success = self.next_success
        form_view.previous_success = self.previous_success
        form_view.previous_failure = self.previous_failure
        form_view.update_success = self.update_success
        form_view.tag_success = self.tag_success
        form_view.show = self.show
        form_view.appstruct = getattr(schema, 'appstruct', None)
        result = form_view()
        return result

    def show(self, form):
        global __tagstruct__
        appstruct = getattr(self.schema, 'appstruct', {})
        self.search_context = self.search_context.constrain(**__tagstruct__)
        appstruct['hit_count'] = self.search_context.hit_count
        state = self.wizard_state.get_step_state(appstruct)
        state = self.deserialize(state)
        log.debug('show, state=%s', state)
        result = dict(form=form.render(appstruct=state))
        return result

    def update_success(self, validated):
        validated = self.serialize(validated)
        self.wizard_state.set_state(self.schema.name, validated)
        #self.wizard_state.increment_step()
        return HTTPFound(location = self.request.path_url)

    def tag_success(self, validated):
        global __tagstruct__

        validated = self.serialize(validated)
        
        # update tags
        facet = validated['facet']
        item = validated['facet_item']
        __tagstruct__[facet] = item
        log.debug('tags = %s' % (__tagstruct__))

        # norrow search
        self.search_context = self.search_context.constrain(**__tagstruct__)
        facets = self.search_context.get_facet_options()
        if len(facets.keys()) > 0:
            validated['facet'] = facets.keys()[0]
        self.wizard_state.set_state(self.schema.name, validated)
        return HTTPFound(location = self.request.path_url)

def workflow_wizard_done(request, states):
    log.debug('states = %s', states)
    #wizard.get_summary(request)
    return {'form' : FormView(request)}

@view_config(route_name='workflow',
             renderer='templates/form.pt',
             layout='default',
             permission='edit',
             )
def workflow_wizard(request):
    # step 0, choose wps
    from .schema import ChooseWorkflowSchema
    schema_0 = ChooseWorkflowSchema()

    # step 1, choose data source
    from .schema import ChooseWorkflowDataSourceSchema
    schema_1 = ChooseWorkflowDataSourceSchema()

    # step 2, seach esgf data
    from .schema import SearchWorkflowEsgfDataSchema
    schema_2 = SearchWorkflowEsgfDataSchema()

    # step 3, enter workflow params
    #schema_3 = WorkflowRunSchema()
    wizard = WorkflowFormWizard('Workflow', workflow_wizard_done, 
                                schema_0, schema_1, schema_2)
    view = WorkflowFormWizardView(wizard)
    return view(request)

@view_config(route_name='help',
             renderer='templates/embedded.pt',
             layout='default',
             permission='view'
             )
def help(request):
    log.debug('rendering help view')
    return dict(external_url='/docs')

