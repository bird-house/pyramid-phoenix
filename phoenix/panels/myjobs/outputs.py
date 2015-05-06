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

    def generate_publish_form(self, formid="deform"):
        """Generate form for publishing to catalog service"""
        from phoenix.schema import PublishSchema
        schema = PublishSchema().bind()
        return Form(
            schema,
            buttons=('publish',),
            formid=formid)

    def process_publish_form(self, form, jobid, tab):
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
        return HTTPFound(location=self.request.route_url('myjobs_details', jobid=jobid, tab=tab))

    def generate_upload_form(self, formid="deform"):
        """Generate form for upload to swift cloud"""
        from phoenix.schema import UploadSchema
        schema = UploadSchema().bind()
        return Form(
            schema,
            buttons=('upload',),
            formid=formid)

    def process_upload_form(self, form, jobid, tab):
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
        return HTTPFound(location=self.request.route_url('myjobs_details', jobid=jobid, tab=tab))
    
    @panel_config(name='myjobs_outputs', renderer='phoenix:templates/panels/myjobs_outputs.pt')
    def panel(self):
        publish_form = self.generate_publish_form()
        upload_form = self.generate_upload_form()

        ## if 'publish' in self.request.POST:
        ##     return self.process_publish_form(publish_form, jobid, tab)
        ## elif 'upload' in self.request.POST:
        ##     return self.process_upload_form(upload_form, jobid, tab)

        return {}
