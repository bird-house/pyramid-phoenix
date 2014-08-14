from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound

from deform import Form, Button

from owslib.wps import WebProcessingService

from string import Template

from phoenix import models
from phoenix.view import MyView
from phoenix.exceptions import MyProxyLogonFailure

import logging
logger = logging.getLogger(__name__)

class WizardState(object):
    def __init__(self, session, initial_step, final_step='wizard_done'):
        self.session = session
        self.initial_step = initial_step
        self.final_step = final_step
        if not 'wizard' in self.session:
            self.clear()
            
    def current_step(self):
        step = self.initial_step
        if len(self.session['wizard']['chain']) > 0:
            step = self.session['wizard']['chain'][-1]
        return step

    def is_first(self):
        return self.current_step() == self.initial_step

    def is_last(self):
        return self.current_step() == self.final_step

    def next(self, step):
        self.session['wizard']['chain'].append(step)
        self.session.changed()

    def previous(self):
        if len(self.session['wizard']['chain']) > 1:
            self.session['wizard']['chain'].pop()
            self.session.changed()

    def get(self, key, default=None):
        if self.session['wizard']['state'].get(key) is None:
            self.session['wizard']['state'][key] = default
            self.session.changed()
        return self.session['wizard']['state'].get(key)

    def set(self, key, value):
        self.session['wizard']['state'][key] = value
        self.session.changed()

    def clear(self):
        self.session['wizard'] = dict(state={}, chain=[self.initial_step])
        self.session.changed()

@view_defaults(permission='view', layout='default')
class Wizard(MyView):
    def __init__(self, request, title, description=None):
        super(Wizard, self).__init__(request, title, description)
        self.csw = self.request.csw
        self.wizard_state = WizardState(self.session, 'wizard_wps')
        self.top_title = "Wizard"
        self.top_route_name = "wizard_wps"
        
    def buttons(self):
        prev_disabled = not self.prev_ok()
        next_disabled = not self.next_ok()

        prev_button = Button(name='previous', title='Previous',
                             disabled=prev_disabled)   #type=submit|reset|button,value=name,css_type="btn-..."
        next_button = Button(name='next', title='Next',
                             disabled=next_disabled)
        done_button = Button(name='next', title='Done',
                             disabled=next_disabled)
        cancel_button = Button(name='cancel', title='Cancel',
                               css_class='btn btn-danger',
                               disabled=False)
        buttons = []
        # TODO: fix focus button
        if not self.wizard_state.is_first():
            buttons.append(prev_button)
        if self.wizard_state.is_last():
            buttons.append(done_button)
        else:
            buttons.append(next_button)
        buttons.append(cancel_button)
        return buttons

    def prev_ok(self):
        return True

    def next_ok(self):
        return True
    
    def use_ajax(self):
        return False

    def ajax_options(self):
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
        return options

    def appstruct(self):
        return {}

    def schema(self):
        raise NotImplementedError

    def previous_success(self, appstruct):
        raise NotImplementedError
    
    def next_success(self, appstruct):
        raise NotImplementedError

    def generate_form(self, formid='deform'):
        return Form(
            schema = self.schema(),
            buttons=self.buttons(),
            formid=formid,
            use_ajax=self.use_ajax(),
            ajax_options=self.ajax_options(),
            )

    def process_form(self, form, action):
        from deform import ValidationFailure
        
        success_method = getattr(self, '%s_success' % action)
        try:
            controls = self.request.POST.items()
            appstruct = form.validate(controls)
            result = success_method(appstruct)
        except ValidationFailure as e:
            logger.exception('Validation of wizard view failed.')
            result = dict(form=e.render())
        return result
        
    def previous(self):
        self.wizard_state.previous()
        return HTTPFound(location=self.request.route_url(self.wizard_state.current_step()))

    def next(self, step):
        self.wizard_state.next(step)
        return HTTPFound(location=self.request.route_url(self.wizard_state.current_step()))

    def cancel(self):
        self.wizard_state.clear()
        return HTTPFound(location=self.request.route_url(self.wizard_state.current_step()))

    def custom_view(self):
        return {}

    def view(self):
        form = self.generate_form()
        
        if 'previous' in self.request.POST:
            return self.process_form(form, 'previous')
        elif 'next' in self.request.POST:
            return self.process_form(form, 'next')
        elif 'cancel' in self.request.POST:
            return self.cancel()
        
        custom = self.custom_view()    
        result = dict(form=form.render(self.appstruct()))

        # custom overwrites result
        return dict(result, **custom)

class ChooseWPS(Wizard):
    def __init__(self, request):
        super(ChooseWPS, self).__init__(request, 'Choose WPS')

    def schema(self):
        from phoenix.schema import ChooseWPSSchema
        return ChooseWPSSchema().bind(wps_list = models.get_wps_list(self.request))

    def success(self, appstruct):
        self.wizard_state.set('wps_url', appstruct.get('url'))

    def previous_success(self, appstruct):
        self.success(appstruct)
        return self.previous()

    def next_success(self, appstruct):
        self.success(appstruct)
        return self.next('wizard_process')

    def appstruct(self):
        return dict(url=self.wizard_state.get('wps_url'))

    @view_config(route_name='wizard_wps', renderer='phoenix:templates/wizard/default.pt')
    def view(self):
        return super(ChooseWPS, self).view()

class ChooseWPSProcess(Wizard):
    def __init__(self, request):
        super(ChooseWPSProcess, self).__init__(request, 'Choose WPS Process')
        self.wps = WebProcessingService(self.wizard_state.get('wps_url'))
        self.description = self.wps.identification.title

    def schema(self):
        from phoenix.schema import SelectProcessSchema
        return SelectProcessSchema().bind(processes = self.wps.processes)

    def success(self, appstruct):
        self.wizard_state.set('process_identifier', appstruct.get('identifier'))

    def previous_success(self, appstruct):
        self.success(appstruct)
        return self.previous()
        
    def next_success(self, appstruct):
        self.success(appstruct)
        return self.next('wizard_literal_inputs')
        
    def appstruct(self):
        return dict(identifier=self.wizard_state.get('process_identifier'))

    @view_config(route_name='wizard_process', renderer='phoenix:templates/wizard/default.pt')
    def view(self):
        return super(ChooseWPSProcess, self).view()

class LiteralInputs(Wizard):
    def __init__(self, request):
        super(LiteralInputs, self).__init__(
            request,
            "Literal Inputs",
            "")
        self.wps = WebProcessingService(self.wizard_state.get('wps_url'))
        self.process = self.wps.describeprocess(self.wizard_state.get('process_identifier'))
        self.description = "Process %s" % self.process.title

    def schema(self):
        from .wps import WPSSchema
        return WPSSchema(info=True, hide_complex=True, process = self.process)

    def success(self, appstruct):
        self.wizard_state.set('literal_inputs', appstruct)

    def previous_success(self, appstruct):
        self.success(appstruct)
        return self.previous()
    
    def next_success(self, appstruct):
        self.success(appstruct)
        return self.next('wizard_complex_inputs')
    
    def appstruct(self):
        return self.wizard_state.get('literal_inputs', {})

    @view_config(route_name='wizard_literal_inputs', renderer='phoenix:templates/wizard/default.pt')
    def view(self):
        return super(LiteralInputs, self).view()

class ComplexInputs(Wizard):
    def __init__(self, request):
        super(ComplexInputs, self).__init__(
            request,
            "Choose Complex Input Parameter",
            "")
        self.wps = WebProcessingService(self.wizard_state.get('wps_url'))
        self.process = self.wps.describeprocess(self.wizard_state.get('process_identifier'))
        self.description = "Process %s" % self.process.title

    def schema(self):
        from phoenix.schema import ChooseInputParamterSchema
        return ChooseInputParamterSchema().bind(process=self.process)

    def success(self, appstruct):
        self.wizard_state.set('complex_input_identifier', appstruct.get('identifier'))
        for input in self.process.dataInputs:
            if input.identifier == appstruct.get('identifier'):
                self.wizard_state.set('mime_types', [value.mimeType for value in input.supportedValues])

    def previous_success(self, appstruct):
        self.success(appstruct)
        return self.previous()

    def next_success(self, appstruct):
        self.success(appstruct)
        return self.next('wizard_source')

    def appstruct(self):
        return dict(identifier=self.wizard_state.get('complex_input_identifier'))

    @view_config(route_name='wizard_complex_inputs', renderer='phoenix:templates/wizard/default.pt')
    def view(self):
        return super(ComplexInputs, self).view()

class ChooseSource(Wizard):
    def __init__(self, request):
        super(ChooseSource, self).__init__(
            request,
            "Choose Source",
            "")
        self.description = self.wizard_state.get('complex_input_identifier')
    def schema(self):
        from phoenix.schema import ChooseSourceSchema
        return ChooseSourceSchema()

    def success(self, appstruct):
        self.wizard_state.set('source', appstruct.get('source'))

    def previous_success(self, appstruct):
        self.success(appstruct)
        return self.previous()

    def next_success(self, appstruct):
        self.success(appstruct)
        return self.next( self.wizard_state.get('source') )
        
    def appstruct(self):
        return dict(source=self.wizard_state.get('source'))

    @view_config(route_name='wizard_source', renderer='phoenix:templates/wizard/default.pt')
    def view(self):
        return super(ChooseSource, self).view()
    
class CatalogSearch(Wizard):
    def __init__(self, request):
        super(CatalogSearch, self).__init__(
            request,
            "CSW Catalog Search")
        self.description = self.wizard_state.get('complex_input_identifier')

    def schema(self):
        from phoenix.schema import CatalogSearchSchema
        return CatalogSearchSchema()

    def success(self, appstruct):
        #self.wizard_state.set('esgf_files', appstruct.get('url'))
        pass

    def previous_success(self, appstruct):
        self.success(appstruct)
        return self.previous()

    def next_success(self, appstruct):
        self.success(appstruct)
        return self.next('wizard_done')

    def search_csw(self, query=''):
        keywords = [k for k in map(str.strip, str(query).split(' ')) if len(k)>0]

        # TODO: search all formats
        format = self.wizard_state.get('mime_types')[0]

        cql_tmpl = Template("""\
        dc:creator='${email}'\
        and dc:format='${format}'
        """)
        cql = cql_tmpl.substitute({
            'email': self.get_user().get('email'),
            'format': format})
        cql_keyword_tmpl = Template('and csw:AnyText like "%${keyword}%"')
        for keyword in keywords:
            cql += cql_keyword_tmpl.substitute({'keyword': keyword})

        results = []
        try:
            self.csw.getrecords(esn="full", cql=cql)
            logger.debug('csw results %s', self.csw.results)
            for rec in self.csw.records:
                myrec = self.csw.records[rec]
                results.append(dict(
                    source = myrec.source,
                    identifier = myrec.identifier,
                    title = myrec.title,
                    abstract = myrec.abstract,
                    subjects = myrec.subjects,
                    format = myrec.format,
                    creator = myrec.creator,
                    modified = myrec.modified,
                    bbox = myrec.bbox,
                    references = myrec.references,
                    ))
        except:
            logger.exception('could not get items for csw.')
        return results
        
    @view_config(renderer='json', name='select.csw')
    def select_csw(self):
        # TODO: refactor this ... not efficient
        identifier = self.request.params.get('identifier', None)
        logger.debug('called with %s', identifier)
        if identifier is not None:
            selection = self.wizard_state.get('csw_selection', [])
            if identifier in selection:
                selection.remove(identifier)
            else:
                selection.append(identifier)
            self.wizard_state.set('csw_selection', selection)
        return {}

    def appstruct(self):
        return dict(csw_selection=self.wizard_state.get('csw_selection'))

    def custom_view(self):
        query = self.request.params.get('query', None)
        checkbox = self.request.params.get('checkbox', None)
        items = self.search_csw(query)
        for item in items:            
            if item['identifier'] in self.wizard_state.get('csw_selection', []):
                item['selected'] = True
            else:
                item['selected'] = False

        from phoenix.grid import CatalogSearchGrid    
        grid = CatalogSearchGrid(
                self.request,
                items,
                ['title', 'format', 'selected'],
            )
        return dict(grid=grid, items=items)

    @view_config(route_name='wizard_csw', renderer='phoenix:templates/wizard/csw.pt')
    def view(self):
        return super(CatalogSearch, self).view()

class ESGFSearch(Wizard):
    def __init__(self, request):
        super(ESGFSearch, self).__init__(
            request,
            "ESGF Search",
            "")

    def schema(self):
        from phoenix.schema import ESGFSearchSchema
        return ESGFSearchSchema()

    def success(self, appstruct):
        self.wizard_state.set('esgf_selection', appstruct.get('selection'))

    def previous_success(self, appstruct):
        self.success(appstruct)
        return self.previous()
        
    def next_success(self, appstruct):
        self.success(appstruct)
        return self.next('wizard_esgf_files')

    def appstruct(self):
        return dict(selection=self.wizard_state.get('esgf_selection', {}))

    @view_config(route_name='wizard_esgf', renderer='phoenix:templates/wizard/esgf.pt')
    def view(self):
        return super(ESGFSearch, self).view()

class ESGFFileSearch(Wizard):
    def __init__(self, request):
        super(ESGFFileSearch, self).__init__(
            request,
            "ESGF File Search",
            "")

    def schema(self):
        from phoenix.schema import ESGFFilesSchema
        return ESGFFilesSchema().bind(selection=self.wizard_state.get('esgf_selection'))

    def success(self, appstruct):
        self.wizard_state.set('esgf_files', appstruct.get('url'))

    def previous_success(self, appstruct):
        self.success(appstruct)
        return self.previous()
        
    def next_success(self, appstruct):
        self.success(appstruct)
        return self.next('wizard_esgf_credentials')
        
    def appstruct(self):
        return dict(url=self.wizard_state.get('esgf_files'))

    @view_config(route_name='wizard_esgf_files', renderer='phoenix:templates/wizard/esgf.pt')
    def view(self):
        return super(ESGFFileSearch, self).view()

class ESGFCredentials(Wizard):
    def __init__(self, request):
        super(ESGFCredentials, self).__init__(
            request,
            "ESGF Credentials",
            "")

    def schema(self):
        from phoenix.schema import CredentialsSchema
        return CredentialsSchema().bind()

    def success(self, appstruct):
        try:
            self.wizard_state.set('password', appstruct.get('password'))
            result = models.myproxy_logon(
                self.request,
                openid=self.get_user().get('openid'),
                password=appstruct.get('password'))
            user = self.get_user()
            user['credentials'] = result['credentials']
            user['cert_expires'] = result['cert_expires'] 
            self.userdb.update({'email':self.user_email()}, user)
        except Exception, e:
            logger.exception("update credentials failed.")
            self.request.session.flash(
                "Could not update your credentials. %s" % (e), queue='error')
        else:
            self.request.session.flash(
                'Credentials updated.', queue='success')
        
    def previous_success(self, appstruct):
        self.success(appstruct)
        return self.previous()
        
    def next_success(self, appstruct):
        self.success(appstruct)
        return self.next('wizard_done')
        
    def appstruct(self):
        return dict(
            openid=self.get_user().get('openid'),
            password=self.wizard_state.get('password'))

    @view_config(route_name='wizard_esgf_credentials', renderer='phoenix:templates/wizard/esgf.pt')
    def view(self):
        return super(ESGFCredentials, self).view()

class Done(Wizard):
    def __init__(self, request):
        super(Done, self).__init__(
            request,
            "Done",
            "Check Parameters and start WPS Process")
        self.wps = WebProcessingService(self.wizard_state.get('wps_url'))
        self.csw = self.request.csw

    def schema(self):
        from phoenix.schema import DoneSchema
        return DoneSchema()

    def sources(self):
        sources = []
        source = self.wizard_state.get('source')
        if source == 'wizard_csw':
            self.csw.getrecordbyid(id=self.wizard_state.get('csw_selection', []))
            sources = [[str(rec.source)] for rec in self.csw.records.values()]
        elif source == 'wizard_esgf':
            sources = [[str(file_url)] for file_url in self.wizard_state.get('esgf_files')]
        return sources

    def workflow_description(self):
        credentials = self.get_user().get('credentials')

        source = dict(
            service = self.request.wps.url,
            identifier = 'esgf_wget',
            input = ['credentials=%s' % (credentials)],
            complex_input = 'source',
            output = ['output'],
            sources = self.sources())
        worker_inputs = map(lambda x: str(x[0]) + '=' + str(x[1]),  self.wizard_state.get('literal_inputs').items())
        worker = dict(
            service = self.wps.url,
            identifier = self.wizard_state.get('process_identifier'),
            input = worker_inputs,
            complex_input = self.wizard_state.get('complex_input_identifier'),
            output = ['output'])
        nodes = dict(source=source, worker=worker)
        return nodes

    def execute_workflow(self, appstruct):
        nodes = self.workflow_description()
        from .wps import execute_restflow
        return execute_restflow(self.request.wps, nodes)

    def success(self, appstruct):
        identifier = self.wizard_state.get('process_identifier')
        notes = self.wizard_state.get('literal_inputs')['info_notes']
        tags = self.wizard_state.get('literal_inputs')['info_tags']
        
        execution = self.execute_workflow(appstruct)
        models.add_job(
            request = self.request,
            title = identifier,
            wps_url = execution.serviceInstance,
            status_location = execution.statusLocation,
            notes = notes,
            tags = tags)

    def previous_success(self, appstruct):
        return self.previous()
    
    def next_success(self, appstruct):
        self.success(appstruct)
        self.wizard_state.clear()
        return HTTPFound(location=self.request.route_url('jobs'))

    @view_config(route_name='wizard_done', renderer='phoenix:templates/wizard/default.pt')
    def view(self):
        return super(Done, self).view()
