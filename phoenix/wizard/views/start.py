import yaml

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.security import authenticated_userid

from owslib.wps import WPSExecution, WebProcessingService

from phoenix.utils import time_ago_in_words
from phoenix.catalog import get_service_name
from phoenix.wizard.views import Wizard

import logging
logger = logging.getLogger(__name__)

def job_to_state(request, job_id):
    # TODO: quite dirty ... needs clean up
    state = {}
    job = request.db.jobs.find_one({'identifier': job_id})
    execution = WPSExecution()
    execution.checkStatus(url=job['status_location'], sleepSecs=0)
    if len(execution.dataInputs) == 1:
        if len(execution.dataInputs[0].data) == 1:
            workflow = yaml.load(execution.dataInputs[0].data[0])

            # TODO: get the correct worker wps url
            # TODO: avoid getcaps
            wps = WebProcessingService(url=workflow['worker']['url'], verify=False, skip_caps=False)
            process = wps.describeprocess(workflow['worker']['identifier'])

            state['wizard_wps'] = {'identifier': get_service_name(request, wps.url)}
            state['wizard_process'] = {'identifier': workflow['worker']['identifier']}
            inputs = {}
            for inp in workflow['worker']['inputs']:
                key, value = inp[0], inp[1]
                if key in inputs:
                    inputs[key].extend(value)
                else:
                    inputs[key] = [value]
            
            for inp in process.dataInputs:
                if 'boolean' in inp.dataType and inp.identifier in result:
                    inputs[inp.identifier] = [ val.lower() == 'true' for val in inputs[inp.identifier]]
                if inp.maxOccurs < 2 and inp.identifier in inputs:
                    inputs[inp.identifier] = inputs[inp.identifier][0]
            state['wizard_literal_inputs'] = inputs
            state['wizard_complex_inputs'] = {'identifier': workflow['worker']['resource']}
            if workflow['name'] == 'wizard_esgf_search':
                state['wizard_source'] = {'source': 'wizard_esgf_search'}
                import json
                state['wizard_esgf_search'] = {'selection': json.dumps(workflow['source']['esgf'])}
            elif workflow['name'] == 'wizard_solr':
                state['wizard_source'] = {'source': 'wizard_solr'}
            elif workflow['name'] == 'wizard_threddsservice':
                state['wizard_source'] = {'source': 'wizard_threddsservice'}
                state['wizard_threddsservice'] = {'url': workflow['source']['thredds']['catalog_url']}
            state['wizard_done'] = {'caption': job.get('caption')}
    return state


import colander
from deform.widget import SelectWidget
class FavoriteSchema(colander.MappingSchema):
    @colander.deferred
    def deferred_favorite_widget(node, kw):
        jobs = kw.get('jobs', [])
        gentitle = lambda job: "{0} - {1} - {2}".format(
            job.get('title'), job.get('caption', '???'),
            time_ago_in_words(job.get('finished')))
        choices = [('', 'No Favorite'), ('last', 'Last')]
        logger.debug('jobs %s', jobs)
        choices.extend( [(job['identifier'], gentitle(job) ) for job in jobs] )
        return SelectWidget(values = choices)

    job_id = colander.SchemaNode(
        colander.String(),
        title = "Favorite",
        missing = '',
        widget = deferred_favorite_widget)

class Start(Wizard):
    def __init__(self, request):
        super(Start, self).__init__(request, name='wizard', title='Choose a Favorite')
        self.collection = request.db.jobs
        self.wizard_state.clear()
            
    def schema(self):
        jobs = []
        # add restarted job
        if 'job_id' in self.request.params:
            job = self.collection.find_one({'identifier': self.request.params['job_id']})
            if job:
                jobs.append( job )
        # search favs
        search_filter = {}
        search_filter['tags'] = 'fav'
        search_filter['is_workflow'] = True
        search_filter['status'] = 'ProcessSucceeded'
        search_filter['userid'] = authenticated_userid(self.request)
        fav_jobs = self.collection.find(search_filter).limit(50).sort([('created', -1)])
        if fav_jobs.count() > 0:
            jobs.extend(list(fav_jobs))
        return FavoriteSchema().bind(jobs=jobs)

    def appstruct(self):
        struct = {}
        if 'job_id' in self.request.params:
            struct['job_id'] =self.request.params['job_id']
        return struct

    def success(self, appstruct):
        job_id = appstruct.get('job_id')
        if job_id:
            if job_id == 'last':
                state = self.favorite.get('last')
            else:
                state = job_to_state(self.request, appstruct.get('job_id'))
            self.wizard_state.load(state)
        super(Start, self).success(appstruct)

    def next_success(self, appstruct):
        self.success(appstruct)
        return self.next('wizard_wps')

    @view_config(route_name='wizard', renderer='../templates/wizard/start.pt')
    def view(self):
        return super(Start, self).view()
