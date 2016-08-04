from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPException, HTTPFound, HTTPNotFound
from deform import Form, Button
from deform import ValidationFailure

from phoenix.events import JobStarted
from phoenix.processes.views import Processes
from phoenix.wps import appstruct_to_inputs
from phoenix.wps import WPSSchema
from phoenix.utils import wps_describe_url
from phoenix.catalog import get_service_name
from phoenix.security import has_execute_permission
# TODO: we need to use the twitcher api
from twitcher.registry import proxy_url


from owslib.wps import WebProcessingService

import logging
logger = logging.getLogger(__name__)

@view_defaults(permission='view', layout='default')
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
        elif 'wps' in request.params:
            self.service_name = request.params.get('wps')
            self.processid = request.params.get('process')
        else:
            self.service_name = None
            self.processid = None
       
        if self.service_name:
            # TODO: avoid getcaps
            self.wps = WebProcessingService(url=proxy_url(request, self.service_name), verify=False)
            # TODO: need to fix owslib to handle special identifiers
            self.process = self.wps.describeprocess(self.processid)
        super(ExecuteProcess, self).__init__(request, name='processes_execute', title='')

    def breadcrumbs(self):
        breadcrumbs = super(ExecuteProcess, self).breadcrumbs()
        if self.service_name:
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
                               css_class='btn btn-default btn-lg btn-block',
                               disabled=not has_execute_permission(self.request, self.service_name))
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
                        metadata=self.process.metadata,
                        form=e.render())
        if self.request.user is None:
            return HTTPFound(location=self.request.route_url('processes_loading'))
        else:
            return HTTPFound(location=self.request.route_url('monitor'))
        
    def execute(self, appstruct):
        inputs = appstruct_to_inputs(self.request, appstruct)
        outputs = []
        for output in self.process.processOutputs:
            outputs.append( (output.identifier, output.dataType == 'ComplexData' ) )

        from phoenix.tasks import execute_process
        result = execute_process.delay(
            userid=self.request.unauthenticated_userid,
            url=self.wps.url,
            identifier=self.process.identifier, 
            inputs=inputs, outputs=outputs)
        self.session['task_id'] = result.id
        self.request.registry.notify(JobStarted(self.request, result.id))

    @view_config(renderer='json', route_name='processes_check_queue')
    def check_queue(self):
        status = 'running'
        task_id = self.session.get('task_id')
        collection = self.request.db.jobs
        if collection.find({"task_id": task_id}).count() == 1:
            status = 'ready'
        return dict(status=status)

    @view_config(route_name='processes_loading', renderer='../templates/processes/loading.pt')
    def loading(self):
        task_id = self.session.get('task_id')
        collection = self.request.db.jobs
        if collection.find({"task_id": task_id}).count() == 1:
            job = collection.find_one({"task_id": task_id})
            return HTTPFound(location=self.request.route_path('monitor_details', tab='log', job_id=job.get('identifier')))
        return {}
    
    @view_config(route_name='processes_execute', renderer='../templates/processes/execute.pt')
    def view(self):
        form = self.generate_form()
        if 'submit' in self.request.POST:
            return self.process_form(form)
        if not has_execute_permission(self.request, self.service_name):
            self.session.flash("You are not allowed to execute processes. Please sign-in.", queue='warning')
        return dict(
            description=getattr(self.process, 'abstract', ''),
            url=wps_describe_url(self.wps.url, self.processid),
            metadata=self.process.metadata,
            form=form.render(self.appstruct()))
    
