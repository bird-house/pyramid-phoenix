from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound
from deform import Form, Button
from deform import ValidationFailure

from phoenix.events import JobStarted
from phoenix.views import MyView
from phoenix.wps import appstruct_to_inputs
from phoenix.wps import WPSSchema
from phoenix.wps import check_status
from phoenix.utils import wps_describe_url
from phoenix.security import has_execute_permission

from owslib.wps import WebProcessingService
from owslib.wps import WPSExecution
from owslib.wps import ComplexDataInput

import logging
logger = logging.getLogger(__name__)


@view_defaults(permission='view', layout='default')
class ExecuteProcess(MyView):
    def __init__(self, request):
        self.request = request
        self.execution = None
        self.service_name = None
        self.processid = None
        self.process = None
        if 'job_id' in request.params:
            job = request.db.jobs.find_one(
                {'identifier': request.params['job_id']})
            self.service_name = job.get('service_name')
            self.execution = check_status(
                url=job.get('status_location'),
                response=job.get('response'),
                verify=False, sleep_secs=0)
            self.processid = self.execution.process.identifier
        elif 'wps' in request.params:
            self.service_name = request.params.get('wps')
            self.processid = request.params.get('process')

        if self.service_name:
            # TODO: avoid getcaps
            self.wps = WebProcessingService(
                url=request.route_url('owsproxy',
                                      service_name=self.service_name),
                verify=False)
            # TODO: need to fix owslib to handle special identifiers
            self.process = self.wps.describeprocess(self.processid)
        super(ExecuteProcess, self).__init__(request, name='processes_execute',
                                             title='')

    def appstruct(self):
        # TODO: not a nice way to get inputs ... should be cleaned up in owslib
        result = {}
        if self.execution:
            for inp in self.execution.dataInputs:
                if inp.data or inp.reference:
                    if inp.identifier not in result:
                        # init result for param with empty list
                        result[inp.identifier] = []
                    if inp.data:
                        # add literal input, inp.data is a list
                        result[inp.identifier].extend(inp.data)
                    elif inp.reference:
                        # add reference to complex input
                        result[inp.identifier].append(inp.reference)
        for inp in self.process.dataInputs:
            # convert boolean
            if 'boolean' in inp.dataType and inp.identifier in result:
                result[inp.identifier] = [val.lower() == 'true' for val in result[inp.identifier]]
            # TODO: very dirty ... if single value then take the first
            if inp.maxOccurs < 2 and inp.identifier in result:
                result[inp.identifier] = result[inp.identifier][0]
        return result

    def generate_form(self, formid='deform'):
        schema = WPSSchema(request=self.request,
                           process=self.process,
                           use_async=self.request.has_permission('submit'),
                           user=self.get_user())
        submit_button = Button(name='submit', title='Execute',
                               css_class='btn btn-success btn-lg btn-block',
                               disabled=not has_execute_permission(
                                    self.request, self.service_name))
        return Form(
            schema,
            buttons=(submit_button,),
            formid=formid,
        )

    def process_form(self, form):
        controls = self.request.POST.items()
        try:
            # TODO: uploader puts qqfile in controls
            controls = [control for control in controls if 'qqfile' not in control[0]]
            logger.debug("before validate %s", controls)
            appstruct = form.validate(controls)
            logger.debug("before execute %s", appstruct)
            self.execute(appstruct)
        except ValidationFailure, e:
            logger.exception('validation of exectue view failed.')
            self.session.flash("There are errors on this page.", queue='danger')
            return dict(process=self.process,
                        url=wps_describe_url(self.wps.url, self.processid),
                        form=e.render())
        if not self.request.user:
            return HTTPFound(location=self.request.route_url('processes_loading'))
        else:
            return HTTPFound(location=self.request.route_url('monitor'))

    def execute(self, appstruct):
        inputs = appstruct_to_inputs(self.request, appstruct)
        # need to use ComplexDataInput
        complex_inpts = []
        for inpt in self.process.dataInputs:
            if 'ComplexData' in inpt.dataType:
                complex_inpts.append(inpt.identifier)
        new_inputs = []
        for inpt in inputs:
            if inpt[0] in complex_inpts:
                new_inputs.append((inpt[0], ComplexDataInput(inpt[1])))
            else:
                new_inputs.append(inpt)
        inputs = new_inputs
        # prepare outputs
        outputs = []
        for output in self.process.processOutputs:
            outputs.append(
                (output.identifier, output.dataType == 'ComplexData'))

        from phoenix.tasks.execute import execute_process
        result = execute_process.delay(
            userid=self.request.unauthenticated_userid,
            url=self.wps.url,
            service_name=self.service_name,
            identifier=self.process.identifier,
            inputs=inputs,
            outputs=outputs,
            async=appstruct.get('_async_check', True))
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
            return HTTPFound(location=self.request.route_path(
                'monitor_details', tab='log', job_id=job.get('identifier')))
        return {}

    @view_config(route_name='processes_execute', renderer='../templates/processes/execute.pt', accept='text/html')
    def view(self):
        form = self.generate_form()
        if 'submit' in self.request.POST:
            return self.process_form(form)
        if not has_execute_permission(self.request, self.service_name):
            self.session.flash("You are not allowed to execute processes. Please sign-in.", queue='warning')
        return dict(
            process=self.process,
            url=wps_describe_url(self.wps.url, self.processid),
            form=form.render(self.appstruct()))
