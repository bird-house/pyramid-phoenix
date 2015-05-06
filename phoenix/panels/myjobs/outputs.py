from pyramid_layout.panel import panel_config

from pyramid.httpexceptions import HTTPFound
from deform import Form
from deform import ValidationFailure

import logging
logger = logging.getLogger(__name__)

class MyJobsOutputs(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.session = self.request.session
    
    def generate_publish_form(self, formid="deform"):
        """Generate form for publishing to catalog service"""
        from phoenix.schema import PublishSchema
        schema = PublishSchema()
        return Form(schema, buttons=('publish',), formid=formid)

    def process_publish_form(self, form, jobid):
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
            self.session.flash("Publication failed. %s" % e, queue='error')
        else:
            self.session.flash("Publication was successful", queue='success')
        return HTTPFound(location=self.request.route_path('myjobs_details', jobid=jobid, tab='outputs'))

    def generate_upload_form(self, formid="deform"):
        """Generate form for upload to swift cloud"""
        from phoenix.schema import UploadSchema
        schema = UploadSchema().bind()
        return Form(
            schema,
            buttons=('upload',),
            formid=formid)

    def process_upload_form(self, form, jobid):
        from phoenix.models import swift
        
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
            self.session.flash("Upload failed. %s" % e, queue='error')
        else:
            self.session.flash("Swift upload added to Jobs.", queue='info')
        return HTTPFound(location=self.request.route_path('myjobs_details', jobid=jobid, tab='outputs'))
    
    @panel_config(name='myjobs_outputs', renderer='phoenix:templates/panels/myjobs_outputs.pt')
    def panel(self):
        jobid = self.session.get('jobid')
        
        publish_form = self.generate_publish_form()
        upload_form = self.generate_upload_form()

        if 'publish' in self.request.POST:
            return self.process_publish_form(publish_form, jobid)
        elif 'upload' in self.request.POST:
            return self.process_upload_form(upload_form, jobid)

        items = []
        from phoenix.models import process_outputs
        for oid,output in process_outputs(self.request, jobid).items():
            items.append(dict(title=output.title,
                              abstract=getattr(output, 'abstract', ""),
                              identifier=oid,
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
