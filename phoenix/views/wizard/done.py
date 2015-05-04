from pyramid.view import view_config

from phoenix.views.wizard import Wizard

import logging
logger = logging.getLogger(__name__)

class Done(Wizard):
    def __init__(self, request):
        super(Done, self).__init__(
            request, name='wizard_done', title="Done")
        self.description = "Describe your Job and start Workflow."
        from owslib.wps import WebProcessingService
        self.wps = WebProcessingService(self.wizard_state.get('wizard_wps')['url'])
        self.csw = self.request.csw

    def schema(self):
        from phoenix.schema import DoneSchema
        return DoneSchema()

    def workflow_description(self, name):
        nodes = {}

        user = self.get_user()
        if 'swift' in name:
            source = dict(
                service = self.request.wps.url,
                storage_url = user.get('swift_storage_url'),
                auth_token = user.get('swift_auth_token'),
            )
            source['container'] = self.wizard_state.get('wizard_swiftbrowser')['container']
            source['prefix'] = self.wizard_state.get('wizard_swiftbrowser')['prefix']
            nodes['source'] = source
            logger.debug('source = %s', source)
        else: # esgsearch
            credentials = user.get('credentials')

            selection = self.wizard_state.get('wizard_esgf')['selection']
            import json
            esgsearch = json.loads(selection)
            nodes['esgsearch'] = esgsearch
            
            source = dict(
                service = self.request.wps.url,
                credentials=credentials,
            )
            nodes['source'] = source

        from phoenix.wps import appstruct_to_inputs
        inputs = appstruct_to_inputs(self.wizard_state.get('wizard_literal_inputs', {}))
        worker_inputs = ['%s=%s' % (key, value) for key,value in inputs]
        worker = dict(
            service = self.wps.url,
            identifier = self.wizard_state.get('wizard_process')['identifier'],
            inputs = [(key, value) for key,value in inputs],
            resource = self.wizard_state.get('wizard_complex_inputs')['identifier'],
            )
        nodes['worker'] = worker
        return nodes

    def execute_workflow(self, appstruct):
        from phoenix.wps import execute_dispel
        source = self.wizard_state.get('wizard_source')['source']
        if 'swift' in source:
            name = 'swift_workflow'
        else:
            name = 'esgsearch_workflow'
        nodes = self.workflow_description(name)
        return execute_dispel(self.request.wps, nodes=nodes, name=name)

    def success(self, appstruct):
        super(Done, self).success(appstruct)
        if appstruct.get('is_favorite', False):
            self.favorite.set(
                name=appstruct.get('favorite_name'),
                state=self.wizard_state.dump())
            self.favorite.save()
        
        execution = self.execute_workflow(appstruct)
        from phoenix.models import add_job
        # TODO: cache process description
        process = self.wps.describeprocess(self.wizard_state.get('wizard_process')['identifier'])
        abstract = None
        if hasattr(process, 'abstract'):
            abstract = process.abstract
        add_job(
            request = self.request,
            workflow = True,
            title = process.title,
            wps_url = execution.serviceInstance,
            status_location = execution.statusLocation,
            abstract = abstract,
            keywords = appstruct.get('keywords'))

    def next_success(self, appstruct):
        from pyramid.httpexceptions import HTTPFound
        self.success(appstruct)
        self.wizard_state.clear()
        return HTTPFound(location=self.request.route_url('myjobs_overview'))

    def appstruct(self):
        appstruct = super(Done, self).appstruct()
        #params = ', '.join(['%s=%s' % item for item in self.wizard_state.get('wizard_literal_inputs', {}).items()])
        identifier = self.wizard_state.get('wizard_process')['identifier']
        # TODO: add search facets to keywords
        appstruct.update( dict(
            keywords="test,workflow,%s" % identifier,
            favorite_name=identifier))
        return appstruct

    @view_config(route_name='wizard_done', renderer='phoenix:templates/wizard/default.pt')
    def view(self):
        return super(Done, self).view()
