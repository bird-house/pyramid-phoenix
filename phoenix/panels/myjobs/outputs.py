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
        self.db = self.request.db

    def collect_outputs(self, status_location, prefix="job"):
        from owslib.wps import WPSExecution
        execution = WPSExecution()
        execution.checkStatus(url=status_location, sleepSecs=0)
        outputs = {}
        for output in execution.processOutputs:
            oid = "%s.%s" %(prefix, output.identifier)
            outputs[oid] = output
        return outputs

    def process_outputs(self, jobid, tab='outputs'):
        job = self.db.jobs.find_one({'identifier': jobid})
        outputs = self.collect_outputs(job['status_location'])
        # TODO: dirty hack for workflows ... not save and needs refactoring
        from owslib.wps import WPSExecution
        execution = WPSExecution()
        execution.checkStatus(url=job['status_location'], sleepSecs=0)
        if job['workflow']:
            import urllib
            import json
            wf_result_url = execution.processOutputs[0].reference
            wf_result_json = json.load(urllib.urlopen(wf_result_url))
            count = 0
            if tab == 'outputs':
                for url in wf_result_json.get('worker', []):
                    count = count + 1
                    outputs = self.collect_outputs(url, prefix='worker%d' % count )
            elif tab == 'resources':
                for url in wf_result_json.get('source', []):
                    count = count + 1
                    outputs = self.collect_outputs(url, prefix='source%d' % count )
            elif tab == 'inputs':
                outputs = {}
        else:
            if tab != 'outputs':
                outputs = {}
        return outputs

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
        tab = 'outputs'
        jobid = self.session.get('jobid')
        
        publish_form = self.generate_publish_form()
        upload_form = self.generate_upload_form()

        if 'publish' in self.request.POST:
            return self.process_publish_form(publish_form, jobid, tab)
        elif 'upload' in self.request.POST:
            return self.process_upload_form(upload_form, jobid, tab)

        items = []
        for oid,output in self.process_outputs(jobid, tab).items():
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

        return dict(grid=grid, items=items)
