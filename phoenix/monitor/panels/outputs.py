from pyramid_layout.panel import panel_config

from pyramid.httpexceptions import HTTPFound
from deform import Form
from deform import ValidationFailure

from phoenix import swift

import logging
logger = logging.getLogger(__name__)

def collect_outputs(status_location):
    from owslib.wps import WPSExecution
    execution = WPSExecution()
    execution.checkStatus(url=status_location, sleepSecs=0)
    outputs = {}
    for output in execution.processOutputs:
        outputs[output.identifier] = output
    return outputs

def process_outputs(request, job_id):
    job = request.db.jobs.find_one({'identifier': job_id})
    outputs = {}
    if job is not None and job.get('is_succeded', False):
        if job.get('is_workflow', False):
            outputs = collect_outputs(job['worker_status_location'])
        else:
            outputs = collect_outputs(job['status_location'])
    return outputs

class Outputs(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.session = self.request.session
    
    def generate_publish_form(self, formid="deform"):
        """Generate form for publishing to catalog service"""
        from phoenix.schema import PublishSchema
        return Form(schema=PublishSchema(), buttons=('publish',), formid=formid)

    def process_publish_form(self, form, job_id):
        try:
            controls = self.request.POST.items()
            appstruct = form.validate(controls)
            
            # TODO: fix template loading and location
            from mako.template import Template
            from os.path import join, dirname
            import phoenix
            templ_dc = Template(filename=join(dirname(phoenix.__file__), "templates", "dc.xml"))

            record=templ_dc.render(**appstruct)
            self.request.csw.transaction(ttype="insert", typename='csw:Record', record=str(record))
        except ValidationFailure, e:
            logger.exception('validation of publish form failed')
            return dict(form=e.render())
        except Exception,e:
            logger.exception("publication failed.")
            self.session.flash("Publication failed. %s" % e, queue='danger')
        else:
            self.session.flash("Publication was successful", queue='success')
        return HTTPFound(location=self.request.route_path('monitor_details', job_id=job_id, tab='outputs'))

    def generate_upload_form(self, formid="deform"):
        """Generate form for upload to swift cloud"""
        from phoenix.schema import UploadSchema
        return Form(schema = UploadSchema(), buttons=('upload',), formid=formid)

    def process_upload_form(self, form, job_id):
        try:
            controls = self.request.POST.items()
            appstruct = form.validate(controls)

            login = swift.swift_login(self.request,
                                username = appstruct.get('username'),
                                password = appstruct.get('password'))
            swift.swift_upload(self.request,
                         storage_url = login.get('storage_url'),
                         auth_token = login.get('auth_token'),
                         container = appstruct.get('container'),
                         prefix = appstruct.get('prefix'),
                         source = appstruct.get('source'))
        except ValidationFailure, e:
            logger.exception('validation of upload form failed')
            return dict(form=e.render())
        except Exception,e:
            logger.exception("upload failed.")
            self.session.flash("Upload failed. %s" % e, queue='danger')
        else:
            self.session.flash("Swift upload added to Jobs.", queue='info')
        return HTTPFound(location=self.request.route_path('monitor_details', job_id=job_id, tab='outputs'))
    
    @panel_config(name='monitor_outputs', renderer='../templates/panels/monitor_outputs.pt')
    def panel(self):
        job_id = self.session.get('job_id')
        
        publish_form = self.generate_publish_form()
        upload_form = self.generate_upload_form()

        if 'publish' in self.request.POST:
            return self.process_publish_form(publish_form, job_id)
        elif 'upload' in self.request.POST:
            return self.process_upload_form(upload_form, job_id)

        items = []
        for output in process_outputs(self.request, job_id).values():
            items.append(dict(title=output.title,
                              abstract=getattr(output, 'abstract', ""),
                              identifier=output.identifier,
                              mime_type = output.mimeType,
                              data = output.data,
                              reference=output.reference))
        items = sorted(items, key=lambda item: item['identifier'], reverse=1)

        from phoenix.grid.processoutputs import ProcessOutputsGrid
        grid = ProcessOutputsGrid(
                self.request,
                items,
                ['output', 'value', ''],
            )

        return dict(grid=grid,
                    publish_form=publish_form.render(),
                    upload_form=upload_form.render())
