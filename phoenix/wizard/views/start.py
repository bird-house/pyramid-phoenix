import yaml

from pyramid.view import view_config
from pyramid.security import authenticated_userid
import colander
from deform.widget import SelectWidget

from owslib.wps import WebProcessingService

from phoenix.wps import check_status
from phoenix.utils import time_ago_in_words
from phoenix.wizard.views import Wizard

import logging
logger = logging.getLogger(__name__)


def includeme(config):
    config.add_route('wizard', '/wizard')
    config.add_view('phoenix.wizard.views.start.Start',
                    route_name='wizard',
                    attr='view',
                    renderer='../templates/wizard/start.pt')


def job_to_state(request, job_id):
    # TODO: quite dirty ... needs clean up
    state = {}
    job = request.db.jobs.find_one({'identifier': job_id})
    execution = check_status(
        url=job.get('status_location'),
        response=job.get('response'),
        verify=False, sleep_secs=0)
    if len(execution.dataInputs) == 1:
        if len(execution.dataInputs[0].data) == 1:
            workflow = yaml.load(execution.dataInputs[0].data[0])

            # TODO: get the correct worker wps url
            # TODO: avoid getcaps
            wps = WebProcessingService(url=workflow['worker']['url'], verify=False, skip_caps=False)
            process = wps.describeprocess(workflow['worker']['identifier'])

            state['wizard_wps'] = {'identifier': request.catalog.get_service_name_by_url(wps.url)}
            state['wizard_process'] = {'identifier': workflow['worker']['identifier']}
            inputs = {}
            for inp in workflow['worker']['inputs']:
                key, value = inp[0], inp[1]
                if key in inputs:
                    inputs[key].extend(value)
                else:
                    inputs[key] = [value]

            for inp in process.dataInputs:
                if 'boolean' in inp.dataType and inp.identifier in inputs:
                    inputs[inp.identifier] = [val.lower() == 'true' for val in inputs[inp.identifier]]
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


class FavoriteSchema(colander.MappingSchema):
    @colander.deferred
    def deferred_favorite_widget(node, kw):
        jobs = kw.get('jobs', [])
        last = kw.get('last', False)
        gentitle = lambda job: "{0} - {1} - {2}".format(
            job.get('title'), job.get('caption', '???'),
            time_ago_in_words(job.get('finished')))
        choices = [('', 'No Favorite')]
        if last:
            choices.append(('last', 'Last Run'))
        logger.debug('jobs %s', jobs)
        choices.extend([(job['identifier'], gentitle(job)) for job in jobs])
        return SelectWidget(values=choices)

    job_id = colander.SchemaNode(
        colander.String(),
        title="Favorite",
        missing='',
        widget=deferred_favorite_widget)


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
                jobs.append(job)
        # add fav jobs
        search_filter = {}
        search_filter['tags'] = 'fav'
        search_filter['is_workflow'] = True
        search_filter['status'] = 'ProcessSucceeded'
        search_filter['userid'] = authenticated_userid(self.request)
        fav_jobs = self.collection.find(search_filter).limit(50).sort([('created', -1)])
        if fav_jobs.count() > 0:
            jobs.extend(list(fav_jobs))
        return FavoriteSchema().bind(jobs=jobs, last='last' in self.favorite.names())

    def appstruct(self):
        struct = {'job_id': 'last'}
        if 'job_id' in self.request.params:
            struct['job_id'] = self.request.params['job_id']
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

    def view(self):
        return super(Start, self).view()
