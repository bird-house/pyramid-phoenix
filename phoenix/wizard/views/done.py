import json

import colander

from pyramid.view import view_config
from pyramid.security import authenticated_userid

from owslib.wps import WebProcessingService
from twitcher.registry import proxy_url

from phoenix.events import JobStarted
from phoenix.wizard.views import Wizard
from phoenix.wps import appstruct_to_inputs
from phoenix.tasks import execute_workflow
from phoenix.tasks import execute_process

import threddsclient

import logging
logger = logging.getLogger(__name__)

class DoneSchema(colander.MappingSchema):
    caption = colander.SchemaNode(
        colander.String(),
        missing = '???')


class Done(Wizard):
    def __init__(self, request):
        super(Done, self).__init__(
            request, name='wizard_done', title="Done")
        self.description = "Describe your Job and start Workflow."
        self.wps = WebProcessingService(proxy_url(request, self.wizard_state.get('wizard_wps')['identifier']),
                                        verify=False, skip_caps=True)

    def breadcrumbs(self):
        breadcrumbs = super(Done, self).breadcrumbs()
        breadcrumbs.append(dict(route_path=self.request.route_path(self.name), title=self.title))
        return breadcrumbs

    def schema(self):
        return DoneSchema().bind()

    def workflow_description(self):
        # source_type
        source_type = self.wizard_state.get('wizard_source')['source']
        workflow = dict(name=source_type, source={}, worker={})

        # source
        user = self.get_user()
        if 'swift' in source_type:
            source = dict(
                storage_url = user.get('swift_storage_url'),
                auth_token = user.get('swift_auth_token'),
            )
            source['container'] = self.wizard_state.get('wizard_swiftbrowser').get('container')
            prefix = self.wizard_state.get('wizard_swiftbrowser').get('prefix')
            logger.debug('swift prefix = %s', prefix)
            if prefix is not None and len(prefix.strip()) > 0:
                source['prefix'] = prefix
            workflow['source']['swift'] = source
        elif 'thredds' in source_type:
            source = dict()
            source['catalog_url'] = self.wizard_state.get('wizard_threddsbrowser').get('url')
            workflow['source']['thredds'] = source
        elif 'esgf' in source_type:
            selection = self.wizard_state.get('wizard_esgf_search')['selection']
            source = json.loads(selection)
            source['url'] = self.request.registry.settings.get('esgfsearch.url')
            source['credentials'] = user.get('credentials')
            workflow['source']['esgf'] = source
        elif 'solr' in source_type:
            state = self.wizard_state.get('wizard_solr')
            source = dict()
            source['url'] = self.request.registry.settings.get('solr.url')
            solr_query = state.get('query', '')
            if len(solr_query.strip()) == 0:
                solr_query = '*:*'
            source['query'] = solr_query
            source['filter_query'] = []
            if state.get('category'):
                source['filter_query'].append( "category:{0}".format(state.get('category')) )
            if state.get('source'):
                source['filter_query'].append( "source:{0}".format(state.get('source')) )
            workflow['source']['solr'] = source
        else:
            raise Exception('Unknown source type')

        # worker
        inputs = appstruct_to_inputs(self.request, self.wizard_state.get('wizard_literal_inputs', {}))
        worker_inputs = ['%s=%s' % (key, value) for key,value in inputs]
        worker = dict(
            url = self.wps.url,
            identifier = self.wizard_state.get('wizard_process')['identifier'],
            inputs = [(key, value) for key,value in inputs],
            resource = self.wizard_state.get('wizard_complex_inputs')['identifier'],
            )
        workflow['worker'] = worker
        return workflow

    def success(self, appstruct):
        super(Done, self).success(appstruct)

        source_type = self.wizard_state.get('wizard_source')['source']
        if source_type == 'wizard_upload':
            inputs = appstruct_to_inputs(self.request, self.wizard_state.get('wizard_literal_inputs', {}))
            resource = self.wizard_state.get('wizard_complex_inputs')['identifier']
            for url in self.wizard_state.get('wizard_storage')['url']:
                inputs.append( (resource, url) )
            result = execute_process.delay(
                userid=authenticated_userid(self.request),
                url=self.wps.url,
                identifier=self.wizard_state.get('wizard_process')['identifier'],
                inputs=inputs, outputs=[])
            self.request.registry.notify(JobStarted(self.request, result.id))
        else:
            result = execute_workflow.delay(
                userid=authenticated_userid(self.request),
                url=self.request.wps.url,
                workflow=self.workflow_description())
            self.request.registry.notify(JobStarted(self.request, result.id))
        
    def next_success(self, appstruct):
        from pyramid.httpexceptions import HTTPFound
        self.success(appstruct)
        self.wizard_state.clear()
        return HTTPFound(location=self.request.route_path('monitor'))

    def appstruct(self):
        appstruct = super(Done, self).appstruct()
        #params = ', '.join(['%s=%s' % item for item in self.wizard_state.get('wizard_literal_inputs', {}).items()])
        identifier = self.wizard_state.get('wizard_process')['identifier']
        appstruct.update( dict(favorite_name=identifier) )
        return appstruct

    @view_config(route_name='wizard_done', renderer='../templates/wizard/default.pt')
    def view(self):
        return super(Done, self).view()
