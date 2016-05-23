from pyramid_layout.panel import panel_config

from pyramid.httpexceptions import HTTPFound
from deform import Form
from deform import ValidationFailure

from phoenix import swift
from phoenix.grid import MyGrid

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

        grid = ProcessOutputsGrid(
                self.request,
                items,
                ['output', 'value', ''],
            )

        return dict(grid=grid,
                    publish_form=publish_form.render(),
                    upload_form=upload_form.render())

class ProcessOutputsGrid(MyGrid):
    def __init__(self, request, *args, **kwargs):
        super(ProcessOutputsGrid, self).__init__(request, *args, **kwargs)
        self.column_formats['output'] = self.output_td
        self.column_formats['value'] = self.value_td
        #self.column_formats['preview'] = self.preview_td
        self.column_formats[''] = self.action_td
        self.exclude_ordering = self.columns

        from string import Template
        url_templ = Template("${url}/Godiva3.html?dataset=outputs")
        base_url = request.registry.settings.get('wms.url')
        self.wms_url = url_templ.substitute({'url': base_url})

    def output_td(self, col_num, i, item):
        return self.render_title_td(
            title=item.get('title'), 
            abstract=item.get('abstract', ""))

    def value_td(self, col_num, i, item):
        return self.render_td(renderer="value_td.mako",
                data=item.get('data', []),
                format=item.get('mime_type'),
                source=item.get('reference'))

    def preview_td(self, col_num, i, item):
        return self.render_preview_td(format=item.get('mime_type'), source=item.get('reference'))

    def action_td(self, col_num, i, item):
        # TODO: dirty hack ...
        buttongroup = []
        if item.get('reference') is not None:
            logger.debug(item.get('reference'))
            if self.request.csw_activated:
                buttongroup.append( ("publish", item.get('identifier'), "glyphicon glyphicon-share", "Publish", "#", False) )
            buttongroup.append( ("view", item.get('identifier'), "glyphicon glyphicon-eye-open", "View", 
                                 item.get('reference', "#"), True) )
            if self.request.wms_activated and 'netcdf' in item.get('mime_type'):
                # TODO: dirty hack for show on map
                if 'wpsoutputs' in item.get('reference'):
                    wms_reference = self.wms_url + item.get('reference').split('wpsoutputs')[1]
                    buttongroup.append( ("mapit", item.get('identifier'), "glyphicon glyphicon-globe", "Show on Map",
                                        wms_reference, True) )
            buttongroup.append( ("upload", item.get('identifier'), "glyphicon glyphicon-upload", "Upload",
                                 "#", False) )
        return self.render_action_td(buttongroup)
