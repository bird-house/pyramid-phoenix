from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound

from deform import Form, Button

from owslib.wps import WebProcessingService

from string import Template

from phoenix import models
from phoenix.views import MyView
from phoenix.grid import MyGrid
from phoenix.views.wizard import Wizard
from phoenix.exceptions import MyProxyLogonFailure

import logging
logger = logging.getLogger(__name__)

class Done(Wizard):
    def __init__(self, request):
        super(Done, self).__init__(
            request,
            "Done",
            "Describe your Job and start Workflow.")
        self.wps = WebProcessingService(self.wizard_state.get('wps_url'))
        self.csw = self.request.csw

    def schema(self):
        from phoenix.schema import DoneSchema
        return DoneSchema().bind(
            title=self.wizard_state.get('process_identifier'),
            abstract=self.wizard_state.get('literal_inputs'),
            keywords="test",
            favorite_name=self.wizard_state.get('process_identifier'))

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
            output = 'output',
            #output = ['output_path=False'], # if local
            sources = self.sources())
        from phoenix.wps import appstruct_to_inputs
        inputs = appstruct_to_inputs(self.wizard_state.get('literal_inputs'))
        worker_inputs = ['%s=%s' % (key, value) for key,value in inputs]
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
        from phoenix.wps import execute_restflow
        return execute_restflow(self.request.wps, nodes)

    def success(self, appstruct):
        self.wizard_state.set('done', appstruct)
        logger.debug("appstruct %s", appstruct)
        if appstruct.get('is_favorite', False):
            self.favorite.set(
                appstruct.get('favorite_name', 'unknown'),
                self.wizard_state.state())
        
        execution = self.execute_workflow(appstruct)
        models.add_job(
            request = self.request,
            workflow = True,
            title = appstruct.get('title'),
            wps_url = execution.serviceInstance,
            status_location = execution.statusLocation,
            abstract = appstruct.get('abstract'),
            keywords = appstruct.get('keywords'))

    def previous_success(self, appstruct):
        self.success(appstruct)
        return self.previous()
    
    def next_success(self, appstruct):
        self.success(appstruct)
        self.wizard_state.clear()
        return HTTPFound(location=self.request.route_url('myjobs'))

    def appstruct(self):
        return self.wizard_state.get('done', {})

    def breadcrumbs(self):
        breadcrumbs = super(Done, self).breadcrumbs()
        breadcrumbs.append(dict(route_name='wizard_done', title=self.title))
        return breadcrumbs

    @view_config(route_name='wizard_done', renderer='phoenix:templates/wizard/default.pt')
    def view(self):
        return super(Done, self).view()
