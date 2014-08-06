from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound
from pyramid.security import authenticated_userid

from deform import Form
from deform import ValidationFailure

from owslib.wps import WebProcessingService

import models

import logging
logger = logging.getLogger(__name__)

@view_defaults(permission='view', layout='default')
class Wizard(object):
    def __init__(self, request, title, description=''):
        self.request = request
        self.title = title
        self.description = description
        self.session = self.request.session
        self.csw = self.request.csw
        self.catalogdb = models.Catalog(self.request)

class ChooseWPS(Wizard):
    def __init__(self, request):
        super(ChooseWPS, self).__init__(request, 'Choose WPS')

    def generate_form(self, formid='deform'):
        from .schema import ChooseWPSSchema
        schema = ChooseWPSSchema().bind(wps_list = self.catalogdb.all_as_tuple())
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
            buttons=('previous', 'next', 'cancel'),
            formid=formid,
            use_ajax=True,
            ajax_options=options,
            )
    def process_form(self, form):
        controls = self.request.POST.items()
        try:
            captured = form.validate(controls)
            url = captured.get('url', '')
            self.session['wizard_wps_url'] = url
            self.session.changed()
        except ValidationFailure, e:
            logger.exception('validation of wps view failed.')
            return dict(title=self.title, description=self.description, form=e.render())
        return HTTPFound(location=self.request.route_url('wizard_process'))

    @view_config(route_name='wizard_wps', renderer='templates/wizard/wps.pt')
    def choose_wps_view(self):
        form = self.generate_form()
        
        if 'previous' in self.request.POST:
            return HTTPFound(location=self.request.route_url('wizard_wps'))
        elif 'next' in self.request.POST:
            return self.process_form(form)
        elif 'cancel' in self.request.POST:
            return HTTPFound(location=self.request.route_url('wizard_wps'))

        return dict(
            title=self.title,
            description=self.description,
            form=form.render())

class SelectProcess(Wizard):
    def __init__(self, request):
        super(SelectProcess, self).__init__(request, 'Select WPS Process')
        self.wps = WebProcessingService(self.session['wizard_wps_url'])

    def generate_form(self, formid='deform'):
        from .schema import SelectProcessSchema
        schema = SelectProcessSchema().bind(processes = self.wps.processes)
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
            buttons=('previous', 'next', 'cancel'),
            formid=formid,
            use_ajax=True,
            ajax_options=options,
            )
    def process_form(self, form):
        controls = self.request.POST.items()
        try:
            captured = form.validate(controls)
            identifier = captured.get('identifier', '')
            self.session['wizard_process_identifier'] = identifier
            self.session.changed()
        except ValidationFailure, e:
            logger.exception('validation of process view failed.')
            return dict(title=self.title, description=self.description, form=e.render())
        return HTTPFound(location=self.request.route_url('wizard_parameters'))

    @view_config(route_name='wizard_process', renderer='templates/wizard/process.pt')
    def select_process_view(self):
        form = self.generate_form()
        
        if 'previous' in self.request.POST:
            return HTTPFound(location=self.request.route_url('wizard_wps'))
        elif 'next' in self.request.POST:
            return self.process_form(form)
        elif 'cancel' in self.request.POST:
            return HTTPFound(location=self.request.route_url('wizard_process'))

        return dict(
            title=self.title,
            description=self.description,
            form=form.render())

class LiteralInputs(Wizard):
    def __init__(self, request):
        super(LiteralInputs, self).__init__(
            request,
            "Literal Inputs",
            "")
        self.wps = WebProcessingService(self.session['wizard_wps_url'])
        self.process = self.wps.describeprocess(self.session['wizard_process_identifier'])

    def generate_form(self, formid='deform'):
        from .wps import WPSSchema
        schema = WPSSchema(info=True, hide=True, process = self.process)
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
            buttons=('previous', 'next', 'cancel'),
            formid=formid,
            use_ajax=True,
            ajax_options=options,
            )
    def process_form(self, form):
        controls = self.request.POST.items()
        try:
            captured = form.validate(controls)
            self.session['wizard_process_parameters'] = captured
            self.session.changed()
        except ValidationFailure, e:
            logger.exception('validation of process parameter failed.')
            return dict(title=self.title, description=self.description, form=e.render())
        return HTTPFound(location=self.request.route_url('wizard_inputs'))

    @view_config(route_name='wizard_parameters', renderer='templates/wizard/parameters.pt')
    def process_parameters_view(self):
        form = self.generate_form()
        
        if 'previous' in self.request.POST:
            return HTTPFound(location=self.request.route_url('wizard_process'))
        elif 'next' in self.request.POST:
            return self.process_form(form)
        elif 'cancel' in self.request.POST:
            return HTTPFound(location=self.request.route_url('wizard_parameters'))

        return dict(
            title=self.title,
            description=self.description,
            form=form.render())

class ComplexInputs(Wizard):
    def __init__(self, request):
        super(ComplexInputs, self).__init__(
            request,
            "Choose Complex Input",
            "")
        self.wps = WebProcessingService(self.session['wizard_wps_url'])
        self.process = self.wps.describeprocess(self.session['wizard_process_identifier'])

    def generate_form(self, formid='deform'):
        from .schema import ChooseInputParamterSchema
        schema = ChooseInputParamterSchema().bind(process=self.process)
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
            buttons=('previous', 'next', 'cancel'),
            formid=formid,
            use_ajax=True,
            ajax_options=options,
            )
    def process_form(self, form):
        controls = self.request.POST.items()
        try:
            captured = form.validate(controls)
            self.session['wizard_complex_input'] = captured['identifier']
            self.session.changed()
        except ValidationFailure, e:
            logger.exception('validation of process parameter failed.')
            return dict(title=self.title, description=self.description, form=e.render())
        return HTTPFound(location=self.request.route_url('wizard_csw'))

    @view_config(route_name='wizard_inputs', renderer='templates/wizard/inputs.pt')
    def complex_parameters_view(self):
        form = self.generate_form()
        
        if 'previous' in self.request.POST:
            return HTTPFound(location=self.request.route_url('wizard_parameters'))
        elif 'next' in self.request.POST:
            return self.process_form(form)
        elif 'cancel' in self.request.POST:
            return HTTPFound(location=self.request.route_url('wizard_inputs'))

        return dict(
            title=self.title,
            description=self.description,
            form=form.render())
    
class CatalogSearch(Wizard):
    def __init__(self, request):
        super(CatalogSearch, self).__init__(
            request,
            "Catalog Search",
            "Search in CSW Catalog Service")

    def search_csw(self, query=''):
        keywords = [k for k in map(str.strip, str(query).split(' ')) if len(k)>0]

        results = []
        try:
            self.csw.getrecords(keywords=keywords)
            logger.debug('csw results %s', self.csw.results)
            for rec in self.csw.records:
                myrec = self.csw.records[rec]
                results.append(dict(
                    identifier = myrec.identifier,
                    title = myrec.title,
                    abstract = myrec.abstract,
                    subjects = myrec.subjects,
                    format = myrec.format,
                    creator = myrec.creator,
                    modified = myrec.modified,
                    bbox = myrec.bbox,
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
            if 'wizard_csw_selection' in self.session:
                if identifier in self.session['wizard_csw_selection']:
                    self.session['wizard_csw_selection'].remove(identifier)
                else:
                    self.session['wizard_csw_selection'].append(identifier)
            else:
                self.session['wizard_csw_selection'] = [identifier]
        return {}

    def next(self):
        return HTTPFound(location=self.request.route_url('wizard_done'))


    @view_config(route_name='wizard_csw', renderer='templates/wizard/csw.pt')
    def csw_view(self):
        if 'previous' in self.request.POST:
            return HTTPFound(location=self.request.route_url('wizard_parameters'))
        elif 'next' in self.request.POST:
            return self.next()
        elif 'cancel' in self.request.POST:
            return HTTPFound(location=self.request.route_url('wizard_csw'))

        query = self.request.params.get('query', None)
        checkbox = self.request.params.get('checkbox', None)
        logger.debug(checkbox)
        items = self.search_csw(query)
        for item in items:            
            if 'wizard_csw_selection' in self.session and  item['identifier'] in self.session['wizard_csw_selection']:
                item['selected'] = True
            else:
                item['selected'] = False

        from .grid import CatalogSearchGrid    
        grid = CatalogSearchGrid(
                self.request,
                items,
                ['title', 'subjects', 'selected'],
            )

        return dict(
            title=self.title, 
            description=self.description,
            grid=grid,
            items=items,
        )

class Done(Wizard):
    def __init__(self, request):
        super(Done, self).__init__(
            request,
            "Done",
            "Check Parameters and start WPS Process")
        self.wps = WebProcessingService(self.session['wizard_wps_url'])

    def done(self):
        identifier = self.session['wizard_process_identifier']
        inputs = self.session['wizard_process_parameters'].items()
        complex_input = self.session['wizard_complex_input']
        for url in self.session['wizard_csw_selection']:
            inputs.append( (complex_input, url) )
        inputs = [(str(key), str(value)) for key,value in inputs]
        outputs = [("output",True)]
        execution = self.wps.execute(identifier, inputs=inputs, output=outputs)
        
        models.add_job(
            request = self.request,
            user_id = authenticated_userid(self.request), 
            identifier = identifier,
            wps_url = self.wps.url,
            execution = execution,
            notes = self.session['wizard_process_parameters']['info_notes'],
            tags = self.session['wizard_process_parameters']['info_tags'])
         
        return HTTPFound(location=self.request.route_url('jobs'))

    @view_config(route_name='wizard_done', renderer='templates/wizard/done.pt')
    def done_view(self):
        if 'previous' in self.request.POST:
            return HTTPFound(location=self.request.route_url('wizard_csw'))
        elif 'done' in self.request.POST:
            return self.done()
        elif 'cancel' in self.request.POST:
            return HTTPFound(location=self.request.route_url('wizard_summary'))

        return dict(
            title=self.title, 
            description=self.description,
            )
