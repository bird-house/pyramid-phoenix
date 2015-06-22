from pyramid.view import view_config, view_defaults
from pyramid.security import authenticated_userid
from pyramid.httpexceptions import HTTPException, HTTPFound, HTTPNotFound
from deform import Form, Button
from deform import ValidationFailure

from phoenix.events import JobStarted
from phoenix.processes.views import Processes
from phoenix.catalog import wps_url

from owslib.wps import WebProcessingService

import logging
logger = logging.getLogger(__name__)

@view_defaults(permission='submit', layout='default')
class ExecuteProcess(Processes):
    def __init__(self, request):
        self.wps_id = request.params.get('wps')
        self.wps = WebProcessingService(url=wps_url(request, self.wps_id))
        identifier = request.params.get('process')
        # TODO: need to fix owslib to handle special identifiers
        self.process = self.wps.describeprocess(identifier)
        super(ExecuteProcess, self).__init__(request, name='processes_execute', title='')

    def breadcrumbs(self):
        breadcrumbs = super(ExecuteProcess, self).breadcrumbs()
        route_path = self.request.route_path('processes_list', _query=[('wps', self.wps_id)])
        breadcrumbs.append(dict(route_path=route_path, title=self.wps.identification.title))
        breadcrumbs.append(dict(route_path=self.request.route_path(self.name), title=self.process.title))
        return breadcrumbs

    def appstruct(self):
        return {}

    def generate_form(self, formid='deform'):
        from phoenix.schema.wps import WPSSchema
        schema = WPSSchema(process = self.process, user=self.get_user())
        return Form(
            schema,
            buttons=('submit',),
            formid=formid,
            )
    
    def process_form(self, form):
        controls = self.request.POST.items()
        try:
            appstruct = form.validate(controls)
            self.execute(appstruct)
        except ValidationFailure, e:
            logger.exception('validation of exectue view failed.')
            self.session.flash("There are errors on this page.", queue='danger')
            return dict(description=getattr(self.process, 'abstract', ''),
                        form = e.render())
        return HTTPFound(location=self.request.route_url('monitor'))

    def execute(self, appstruct):
        from phoenix.utils import appstruct_to_inputs
        inputs = appstruct_to_inputs(appstruct)
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
            form=form.render(self.appstruct()))
    
