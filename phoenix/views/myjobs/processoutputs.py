from pyramid.view import view_config, view_defaults

from pyramid.httpexceptions import HTTPException, HTTPFound, HTTPNotFound
from deform import Form, Button
from deform import ValidationFailure

from phoenix.views.myjobs import MyJobs

import logging
logger = logging.getLogger(__name__)

@view_defaults(permission='edit', layout='default')
class ProcessOutputs(MyJobs):
    def __init__(self, request):
        super(ProcessOutputs, self).__init__(
            request, name='process_outputs', title='Process Outputs')
        self.db = self.request.db

    def sort_order(self):
        """Determine what the current sort parameters are.
        """
        order = self.request.GET.get('order_col', 'identifier')
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

    def process_form(self, form, jobid):
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
        return HTTPFound(location=self.request.route_url('process_outputs', jobid=jobid))

    def collect_outputs(self, status_location, prefix="job"):
        from owslib.wps import WPSExecution
        execution = WPSExecution()
        execution.checkStatus(url=status_location, sleepSecs=0)
        outputs = {}
        for output in execution.processOutputs:
            oid = "%s.%s" %(prefix, output.identifier)
            outputs[oid] = output
        return outputs

    def process_outputs(self, jobid):
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
            for url in wf_result_json.get('worker', []):
                count = count + 1
                outputs.update( self.collect_outputs(url, prefix='worker%d' % count ))
            count = 0
            for url in wf_result_json.get('source', []):
                count = count + 1
                outputs.update( self.collect_outputs(url, prefix='source%d' % count ))
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

    @view_config(route_name='process_outputs', renderer='phoenix:templates/process_outputs.pt')
    def view(self):
        order = self.sort_order()
        key=order.get('order')
        direction=order.get('order_dir')
        
        form = self.generate_form()

        # TODO: this is a bit fishy ...
        jobid = self.request.matchdict.get('jobid')
        if jobid is not None:
            self.session['jobid'] = jobid
            self.session.changed()

        if 'publish' in self.request.POST:
            return self.process_form(form, jobid)

        items = []
        for oid,output in self.process_outputs(self.session.get('jobid')).items():
            items.append(dict(title=output.title,
                              abstract=getattr(output, 'abstract', ""),
                              identifier=oid,
                              mime_type = output.mimeType,
                              data = output.data,
                              reference=output.reference))
        items = sorted(items, key=lambda item: item[key], reverse=direction==1)
            
        grid = ProcessOutputsGrid(
                self.request,
                items,
                ['output', 'identifier', 'preview', ''],
            )
        return dict(grid=grid, items=items, form=form.render())
        
from phoenix.grid import MyGrid

class ProcessOutputsGrid(MyGrid):
    def __init__(self, request, *args, **kwargs):
        super(ProcessOutputsGrid, self).__init__(request, *args, **kwargs)
        self.column_formats['output'] = self.output_td
        self.column_formats['preview'] = self.preview_td
        self.column_formats[''] = self.action_td
        self.exclude_ordering = ['output', '', 'preview', 'action', '_numbered']

    def output_td(self, col_num, i, item):
        return self.render_title_td(
            title=item.get('title'), 
            abstract=item.get('abstract', ""),
            data=item.get('data', []),
            format=item.get('mime_type'),
            source=item.get('reference'))

    def preview_td(self, col_num, i, item):
        return self.render_preview_td(format=item.get('mime_type'), source=item.get('reference'))

    def action_td(self, col_num, i, item):
        # TODO: dirty hack ...
        wms_url = "http://localhost:8080/thredds/godiva2/godiva2.html?server=http://localhost:8080/thredds/wms/test"
        
        buttongroup = []
        if item.get('reference') is not None:
            wms_reference = wms_url + item.get('reference').split('wpsoutputs')[1]
            buttongroup.append( ("publish", item.get('identifier'), "icon-share", "Publish", "#") )
            buttongroup.append( ("view", item.get('identifier'), "icon-eye-open", "View", 
                                 item.get('reference', "#")) )
            buttongroup.append( ("mapit", item.get('identifier'), "icon-globe", "Show on Map",
                                 wms_reference) )
        return self.render_action_td(buttongroup)

