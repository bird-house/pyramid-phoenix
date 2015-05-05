from pyramid.view import view_config, view_defaults

from pyramid.httpexceptions import HTTPException, HTTPFound, HTTPNotFound
from deform import Form, Button
from deform import ValidationFailure

from phoenix.views.processes import Processes

from owslib.wps import WebProcessingService

import logging
logger = logging.getLogger(__name__)

@view_defaults(permission='edit', layout='default')
class ExecuteProcess(Processes):
    def __init__(self, request):
        url = request.params.get('url')
        # TODO: fix owslib.wps url handling
        url = url.split('?')[0]
        self.wps = WebProcessingService(url)
        identifier = request.params.get('identifier')
        logger.debug("execute: url=%s, identifier=%s", url, identifier)
        # TODO: need to fix owslib to handle special identifiers
        self.process = self.wps.describeprocess(identifier)
        super(ExecuteProcess, self).__init__(request, name='processes_execute', title=self.process.title)
        self.description = getattr(self.process, 'abstract', '')

    def breadcrumbs(self):
        breadcrumbs = super(ExecuteProcess, self).breadcrumbs()
        route_path = self.request.route_path('processes_list', _query=[('url', self.wps.url)] )
        breadcrumbs.append(dict(route_path=route_path, title=self.wps.identification.title))
        breadcrumbs.append(dict(route_path=self.request.route_path(self.name), title=self.title))
        return breadcrumbs

    def appstruct(self):
        return dict(
            title = self.process.title,
            abstract = getattr(self.process, 'abstract', ""),
            keywords = "test,%s,%s" % (self.wps.identification.title, self.process.identifier))

    def generate_form(self, formid='deform'):
        from phoenix.wps import WPSSchema
        schema = WPSSchema(info=True, process = self.process, user=self.get_user())
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
            execution = execute(self.wps, self.process.identifier, appstruct)

            from phoenix.models import add_job
            add_job(
                request = self.request,
                workflow = False,
                title = execution.process.title,
                wps_url = execution.serviceInstance,
                status_location = execution.statusLocation,
                abstract = execution.process.abstract,
                keywords = appstruct.get('keywords', ''))
        except ValidationFailure, e:
            logger.exception('validation of exectue view failed.')
            self.session.flash("There are errors on this page.", queue='error')
            return dict(form = e.render())
        return HTTPFound(location=self.request.route_url('myjobs_overview'))

    @view_config(route_name='processes_execute', renderer='phoenix:templates/execute_process.pt')
    def view(self):
        form = self.generate_form()
        if 'submit' in self.request.POST:
            return self.process_form(form)
        return dict(form=form.render(self.appstruct()))
    
