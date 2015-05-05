from pyramid.view import view_config, view_defaults

from pyramid.httpexceptions import HTTPException, HTTPFound, HTTPNotFound
from deform import Form, Button
from deform import ValidationFailure

from phoenix.views.myjobs import MyJobs

import logging
logger = logging.getLogger(__name__)

@view_defaults(permission='edit', layout='default')
class JobDetails(MyJobs):
    def __init__(self, request):
        super(JobDetails, self).__init__(
            request, name='myjobs_details', title='Job Details')
        self.db = self.request.db

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
 
    @view_config(renderer='json', name='publish.output')
    def publish(self):
        import uuid
        outputid = self.request.params.get('outputid')
        # TODO: why use session for jobid?
        jobid = self.session.get('jobid')
        result = dict()
        if outputid is not None:
            output = self.process_outputs(jobid).get(outputid)

            # TODO: how about schema.bind?
            result = dict(
                identifier = uuid.uuid4().get_urn(),
                title = output.title,
                abstract = getattr(output, "abstract", ""),
                creator = self.user_email(),
                source = output.reference,
                format = output.mimeType,
                keywords = 'one,two,three',
                )

        return result

    @view_config(renderer='json', name='upload.output')
    def upload(self):
        outputid = self.request.params.get('outputid')
        # TODO: why use session for jobid?
        jobid = self.session.get('jobid')
        result = dict()
        if outputid is not None:
            output = self.process_outputs(jobid).get(outputid)
            user = self.get_user()

            result = dict(
                username = user.get('swift_username'),
                container = 'WPS Outputs',
                prefix = jobid,
                source = output.reference,
                format = output.mimeType,
                )

        return result

    @view_config(route_name='myjobs_details', renderer='phoenix:templates/myjobs/details.pt')
    def view(self):
        publish_form = self.generate_publish_form()
        upload_form = self.generate_upload_form()

        tab = self.request.matchdict.get('tab')
        # TODO: this is a bit fishy ...
        jobid = self.request.matchdict.get('jobid')
        if jobid is not None:
            self.session['jobid'] = jobid
            self.session.changed()

        if 'publish' in self.request.POST:
            return self.process_publish_form(publish_form, jobid, tab)
        elif 'upload' in self.request.POST:
            return self.process_upload_form(upload_form, jobid, tab)

        items = []
        for oid,output in self.process_outputs(self.session.get('jobid'), tab).items():
            items.append(dict(title=output.title,
                              abstract=getattr(output, 'abstract', ""),
                              identifier=oid,
                              mime_type = output.mimeType,
                              data = output.data,
                              reference=output.reference))
        items = sorted(items, key=lambda item: item['identifier'], reverse=1)
            
        grid = ProcessOutputsGrid(
                self.request,
                items,
                ['output', 'value', ''],
            )
        return dict(active=tab, jobid=jobid, grid=grid, items=items,
                    publish_form=publish_form.render(),
                    upload_form=upload_form.render())
        
from phoenix.grid import MyGrid

class ProcessOutputsGrid(MyGrid):
    def __init__(self, request, *args, **kwargs):
        super(ProcessOutputsGrid, self).__init__(request, *args, **kwargs)
        self.column_formats['output'] = self.output_td
        self.column_formats['value'] = self.value_td
        #self.column_formats['preview'] = self.preview_td
        self.column_formats[''] = self.action_td
        self.exclude_ordering = self.columns

        from string import Template
        url_templ = Template("${url}/godiva2/godiva2.html?server=${url}/wms/test")
        thredds_url = request.registry.settings.get('thredds.url')
        self.wms_url = url_templ.substitute({'url': thredds_url})

    def output_td(self, col_num, i, item):
        return self.render_title_td(
            title=item.get('title'), 
            abstract=item.get('abstract', ""))

    def value_td(self, col_num, i, item):
        return self.render_td(renderer="value_td",
                data=item.get('data', []),
                format=item.get('mime_type'),
                source=item.get('reference'))

    def preview_td(self, col_num, i, item):
        return self.render_preview_td(format=item.get('mime_type'), source=item.get('reference'))

    def action_td(self, col_num, i, item):
        # TODO: dirty hack ...
        buttongroup = []
        if item.get('reference') is not None:
            # TODO: dirty hack for show on map
            wms_reference = self.wms_url + item.get('reference').split('wpsoutputs')[1]
            buttongroup.append( ("publish", item.get('identifier'), "glyphicon glyphicon-share", "Publish", "#", False) )
            buttongroup.append( ("view", item.get('identifier'), "glyphicon glyphicon-eye-open", "View", 
                                 item.get('reference', "#"), True) )
            buttongroup.append( ("mapit", item.get('identifier'), "glyphicon glyphicon-globe", "Show on Map",
                                 wms_reference, True) )
            buttongroup.append( ("upload", item.get('identifier'), "glyphicon glyphicon-upload", "Upload",
                                 "#", False) )
        return self.render_action_td(buttongroup)

