from pyramid.view import view_config, view_defaults

from pyramid.httpexceptions import HTTPException, HTTPFound, HTTPNotFound
from deform import Form, Button
from deform import ValidationFailure

from phoenix.views import MyView

import logging
logger = logging.getLogger(__name__)

@view_defaults(permission='edit', layout='default')
class ProcessOutputs(MyView):
    def __init__(self, request):
        super(ProcessOutputs, self).__init__(request, 'Process Outputs')

        self.db = self.request.db

    def sort_order(self):
        """Determine what the current sort parameters are.
        """
        order = self.request.GET.get('order_col', 'title')
        order_dir = self.request.GET.get('order_dir', 'asc')
        order_dir = 1 if order_dir == 'asc' else -1
        return dict(order=order, order_dir=order_dir)   

    def generate_form(self, formid="deform"):
        """Generate form for publishing to catalog service"""
        from phoenix.schema import PublishSchema
        schema = PublishSchema().bind()
        return Form(
            schema,
            buttons=('publish',),
            formid=formid)

    def process_form(self, form):
        try:
            controls = self.request.POST.items()
            appstruct = form.validate(controls)

            from mako.template import Template
            templ_dc = Template(filename=os.path.join(os.path.dirname(__file__), "templates", "dc.xml"))

            record=templ_dc.render(**appstruct)
            self.request.csw.transaction(ttype="insert", typename='csw:Record', record=str(record))
        except ValidationFailure, e:
            logger.exception('validation of publish form failed')
            return dict(form=e.render())
        except:
            msg = 'Publication failed.'
            logger.exception(msg)
            self.session.flash(msg, queue='error')
        else:
            self.session.flash("Publication was successful", queue='success')
        return HTTPFound(location=self.request.route_url('output_details'))

    def process_outputs(self, jobid):
        from owslib.wps import WPSExecution
        
        job = self.db.jobs.find_one({'identifier': jobid})
        execution = WPSExecution(url=job['wps_url'])
        execution.checkStatus(url=job['status_location'], sleepSecs=0)
        self.description = execution.process.title
        return execution.processOutputs

    def process_output(self, jobid, outputid):
        process_outputs = self.process_outputs(jobid)
        output = next(o for o in process_outputs if o.identifier == outputid)
        return output
    
    @view_config(renderer='json', name='publish.output')
    def publish(self):
        import uuid
        outputid = self.request.params.get('outputid')
        # TODO: why use session for joid?
        jobid = self.session.get('jobid')
        result = dict()
        if identifier is not None:
            output = self.process_output(jobid, outputid)

            # TODO: who about schema.bind?
            result = dict(
                identifier = uuid.uuid4().get_urn(),
                title = output.title,
                abstract = 'nix',
                creator = self.user_email(),
                source = output.reference,
                format = output.mimeType,
                keywords = 'one,two,three',
                )

        return result

    def breadcrumbs(self):
        breadcrumbs = super(ProcessOutputs, self).breadcrumbs()
        breadcrumbs.append(dict(route_name='myjobs', title="My Jobs"))
        breadcrumbs.append(dict(route_name='process_outputs', title=self.title))
        return breadcrumbs
        
    @view_config(route_name='process_outputs', renderer='phoenix:templates/process_outputs.pt')
    def view(self):
        form = self.generate_form()

        if 'publish' in self.request.POST:
            return self.process_form(form)

        # TODO: this is a bit fishy ...
        if self.request.params.get('jobid') is not None:
            self.session['jobid'] = self.request.params.get('jobid')
            self.session.changed()

        items = []
        for output in self.process_outputs(self.session.get('jobid')):
            items.append(dict(title=output.title,
                              identifier=output.identifier,
                              mime_type = output.mimeType,
                              data = output.data,
                              reference=output.reference))

        from phoenix.grid import OutputDetailsGrid
        grid = OutputDetailsGrid(
                self.request,
                items,
                ['identifier', 'title', 'data', 'reference', 'mime_type', 'action'],
            )
        return dict(grid=grid, items=items, form=form.render())
        
