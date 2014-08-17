from pyramid.view import view_config, view_defaults

from pyramid.httpexceptions import HTTPException, HTTPFound, HTTPNotFound
from deform import Form, Button
from deform import ValidationFailure

from phoenix.views import MyView

import logging
logger = logging.getLogger(__name__)

@view_defaults(permission='edit', layout='default')
class ExecuteProcess(MyView):
    def __init__(self, request):
        super(ExecuteProcess, self).__init__(request, 'Execute')

        self.db = self.request.db
        self.identifier = self.request.matchdict.get('identifier')

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

            from phoenix.wps import execute
            execution = execute(self.wps, self.identifier, appstruct)

            from phoenix.models import add_job
            add_job(
                request = self.request,
                title = execution.process.title,
                wps_url = execution.serviceInstance,
                status_location = execution.statusLocation,
                abstract = appstruct.get('abstract', ''),
                keywords = appstruct.get('keywords', ''))
        except ValidationFailure, e:
            logger.exception('validation of exectue view failed.')
            self.session.flash("There are errors on this page.", queue='error')
            return dict(form = e.render())
        return HTTPFound(location=self.request.route_url('myjobs'))

    def breadcrumbs(self):
        breadcrumbs = super(ExecuteProcess, self).breadcrumbs()
        breadcrumbs.append(dict(route_name='processes', title="Processes"))
        breadcrumbs.append(dict(route_name='execute_process', title=self.title))
        return breadcrumbs

    @view_config(route_name='execute_process', renderer='phoenix:templates/execute_process.pt')
    def view(self):
        form = self.generate_form()
        if 'submit' in self.request.POST:
            return self.process_form(form)
        return dict(form=form.render())
    
