from pyramid.view import view_config, view_defaults
from pyramid.security import authenticated_userid
from pyramid.httpexceptions import HTTPException, HTTPFound, HTTPNotFound
from deform import Form, Button
from deform import ValidationFailure

from phoenix.events import JobStarted
from phoenix.processes.views import Processes
from phoenix.wps import appstruct_to_inputs
from phoenix.wps import WPSSchema
from phoenix.utils import wps_describe_url
from phoenix.catalog import get_service_name
from twitcher.registry import proxy_url

from owslib.wps import WebProcessingService

import logging
logger = logging.getLogger(__name__)

@view_defaults(permission='edit', layout='default')
class ExecuteProcess(Processes):
    def __init__(self, request):
        self.execution = None
        if 'job_id' in request.params:
            job = request.db.jobs.find_one({'identifier': request.params['job_id']})
            from owslib.wps import WPSExecution
            self.execution = WPSExecution()
            self.execution.checkStatus(url=job['status_location'], sleepSecs=0)
            self.processid = self.execution.process.identifier
            self.service_name = get_service_name(request, url=self.execution.serviceInstance)
        else:
            self.service_name = request.params.get('wps')
            self.processid = request.params.get('process')
        # TODO: avoid getcaps
        self.wps = WebProcessingService(url=proxy_url(request, self.service_name), verify=False)
        # TODO: need to fix owslib to handle special identifiers
        self.process = self.wps.describeprocess(self.processid)
        super(ExecuteProcess, self).__init__(request, name='processes_execute', title='')

    def breadcrumbs(self):
        breadcrumbs = super(ExecuteProcess, self).breadcrumbs()
        route_path = self.request.route_path('processes_list', _query=[('wps', self.service_name)])
        breadcrumbs.append(dict(route_path=route_path, title=self.wps.identification.title))
        breadcrumbs.append(dict(route_path=self.request.route_path(self.name), title=self.process.title))
        return breadcrumbs

    def appstruct(self):
        # TODO: not a nice way to get inputs ... should be cleaned up in owslib
        result = {}
        if self.execution:
            for inp in self.execution.dataInputs:
                values = None
                if len(inp.data) > 0:
                    values = inp.data
                elif inp.reference is not None:
                    values = [{'url': inp.reference}]
                if values is not None:
                    if inp.identifier in result:
                        result[inp.identifier].extend(values)
                    else:
                        result[inp.identifier] = values
        for inp in self.process.dataInputs:
            if 'boolean' in inp.dataType and inp.identifier in result:
                result[inp.identifier] = [ val.lower() == 'true' for val in result[inp.identifier]]
            if inp.maxOccurs < 2 and inp.identifier in result:
                result[inp.identifier] = result[inp.identifier][0]
        return result

    def generate_form(self, formid='deform'):
        schema = WPSSchema(request=self.request, process=self.process, user=self.get_user())
        submit_button = Button(name='submit', title='Execute',
                               css_class='btn btn-default',
                               disabled=not self.request.has_permission('submit'))
        return Form(
            schema,
            buttons=(submit_button,),
            formid=formid,
            )
    
    def process_form(self, form):
        controls = self.request.POST.items()
        try:
            logger.debug("before validate %s", controls)
            appstruct = form.validate(controls)
            logger.debug("before execute %s", appstruct)
            self.execute(appstruct)
        except ValidationFailure, e:
            logger.exception('validation of exectue view failed.')
            self.session.flash("There are errors on this page.", queue='danger')
            return dict(description=getattr(self.process, 'abstract', ''),
                        url=wps_describe_url(self.wps.url, self.processid),
                        form=e.render())
        return HTTPFound(location=self.request.route_url('monitor'))

    def execute(self, appstruct):
        inputs = appstruct_to_inputs(self.request, appstruct)
        outputs = []
        for output in self.process.processOutputs:
            outputs.append( (output.identifier, output.dataType == 'ComplexData' ) )

        from phoenix.tasks import execute_process
        result = execute_process.delay(
            userid=authenticated_userid(self.request),
            url=self.wps.url,
            identifier=self.process.identifier, 
            inputs=inputs, outputs=outputs)
        self.request.registry.notify(JobStarted(self.request, result.id))
    
    @view_config(route_name='processes_execute', renderer='../templates/processes/execute.pt')
    def view(self):
        form = self.generate_form()
        if 'submit' in self.request.POST:
            return self.process_form(form)
        return dict(
            description=getattr(self.process, 'abstract', ''),
            url=wps_describe_url(self.wps.url, self.processid),
            form=form.render(self.appstruct()))
    
