import yaml

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from owslib.wps import WPSExecution

from phoenix.wizard.views import Wizard

import logging
logger = logging.getLogger(__name__)

import colander
from deform.widget import SelectWidget
class Schema(colander.MappingSchema):
    @colander.deferred
    def deferred_favorite_widget(node, kw):
        favorites = kw.get('favorites', ['No Favorite'])
        choices = [(item, item) for item in favorites]
        return SelectWidget(values = choices)

    favorite = colander.SchemaNode(
        colander.String(),
        widget = deferred_favorite_widget)

class Start(Wizard):
    def __init__(self, request):
        super(Start, self).__init__(request, name='wizard', title='Choose a Favorite')
        self.wizard_state.clear()
        self.favorite.load()

        self.workflow = None
        if 'job_id' in request.params:
            job = request.db.jobs.find_one({'identifier': request.params['job_id']})
            execution = WPSExecution()
            execution.checkStatus(url=job['status_location'], sleepSecs=0)
            if len(execution.dataInputs) == 1:
                if len(execution.dataInputs[0].data) == 1:
                    self.workflow = yaml.load(execution.dataInputs[0].data[0])
                    logger.debug('workflow = %s', self.workflow)
                    state = {}
                    state['wizard_wps'] = {'identifier': u'urn:uuid:eff95915-eba8-4358-8a6f-1ab947e65ce5'}
                    state['wizard_process'] = {'identifier': self.workflow['worker']['identifier']}
                    state['wizard_literal_inputs'] = {}
                    state['wizard_complex_inputs'] = {'identifier': self.workflow['worker']['resource']}
                    if self.workflow['name'] == 'wizard_esgf_search':
                        state['wizard_source'] = {'source': 'wizard_esgf_search'}
                        #state[self.workflow['name']] = {'selection': self.workflow['source']['esgf']}
                    elif self.workflow['name'] == 'wizard_solr':
                        state['wizard_source'] = {'source': 'wizard_solr'}
                    elif self.workflow['name'] == 'wizard_threddsservice':
                        state['wizard_source'] = {'source': 'wizard_threddsservice'}
                        state['wizard_threddsservice'] = {'url': self.workflow['source']['thredds']['catalog_url']}
                    self.favorite.set(name=self.workflow['worker']['identifier'], state=state)
            
    def schema(self):
        favorites = self.favorite.names()
        return Schema().bind(favorites=favorites)

    def appstruct(self):
        result = {}
        if self.workflow:
            result = {'favorite': self.workflow['worker']['identifier']}
        return result

    def success(self, appstruct):
        favorite_state = self.favorite.get(appstruct.get('favorite'))
        self.wizard_state.load(favorite_state)
        super(Start, self).success(appstruct)

    def next_success(self, appstruct):
        self.success(appstruct)
        return self.next('wizard_wps')

    @view_config(route_name='wizard_clear_favorites')
    def clear_favorites(self):
        self.favorite.drop()
        return HTTPFound(location=self.request.route_path('wizard'))

    @view_config(route_name='wizard', renderer='../templates/wizard/start.pt')
    def view(self):
        return super(Start, self).view()
