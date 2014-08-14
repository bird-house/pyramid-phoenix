from pyramid.view import view_config, view_defaults

from pyramid.httpexceptions import HTTPException, HTTPFound, HTTPNotFound
from deform import Form, Button
from deform import ValidationFailure

from phoenix.view import MyView

import logging
logger = logging.getLogger(__name__)

@view_defaults(permission='edit', layout='default')
class ExecuteProcess(MyView):
    def __init__(self, request):
        super(ExecuteProcess, self).__init__(request, 'Execute')
        self.top_title = "Processes"
        self.top_route_name = "processes"

        self.db = self.request.db
        self.identifier = self.request.params.get('identifier', None)

        from owslib.wps import WebProcessingService
        
        self.wps = self.request.wps
        if 'wps.url' in self.session:
            url = self.session['wps.url']
            self.wps = WebProcessingService(url)
        self.process = self.wps.describeprocess(self.identifier)
        self.description = self.process.title

    def generate_form(self, formid='deform'):
        from phoenix.wps import WPSSchema
        # TODO: should be WPSSchema.bind() ...
        schema = WPSSchema(info=True, process = self.process)
        return Form(
            schema,
            buttons=('submit',),
            formid=formid,
            )
    
    def process_form(self, form):
        controls = self.request.POST.items()
        try:
            appstruct = form.validate(controls)

            from .helpers import execute_wps
            execution = execute_wps(self.wps, self.identifier, appstruct)

            from phoenix.models import add_job
            add_job(
                request = self.request,
                title = execution.process.title,
                wps_url = execution.serviceInstance,
                status_location = execution.statusLocation,
                notes = appstruct.get('info_notes', ''),
                tags = appstruct.get('info_tags', ''))
        except ValidationFailure, e:
            logger.exception('validation of exectue view failed.')
            return dict(form = e.render())
        return HTTPFound(location=self.request.route_url('myjobs'))

    @view_config(route_name='execute_process', renderer='phoenix:templates/execute_process.pt')
    def execute_view(self):
        form = self.generate_form()
        if 'submit' in self.request.POST:
            return self.process_form(form)
        return dict(form=form.render())
    
