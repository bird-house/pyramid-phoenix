import yaml

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from owslib.wps import WPSExecution, WebProcessingService

from phoenix.catalog import wps_id
from phoenix.wizard.views import Wizard

import logging
logger = logging.getLogger(__name__)

def job_to_state(request):
    # TODO: quite dirty ... needs clean up
    state = {}
    job = request.db.jobs.find_one({'identifier': request.params['job_id']})
    execution = WPSExecution()
    execution.checkStatus(url=job['status_location'], sleepSecs=0)
    if len(execution.dataInputs) == 1:
        if len(execution.dataInputs[0].data) == 1:
            workflow = yaml.load(execution.dataInputs[0].data[0])

            # TODO: get the correct worker wps url
            # TODO: avoid getcaps
            wps = WebProcessingService(url=workflow['worker']['url'].split('?')[0], verify=False, skip_caps=False)
            process = wps.describeprocess(workflow['worker']['identifier'])
           
            state['wizard_wps'] = {'identifier': wps_id(request, wps.identification.title)}
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
    return state


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

        if 'job_id' in request.params:
            state = job_to_state(request)
            self.favorite.set(name='restart', state=state)
            
    def schema(self):
        favorites = self.favorite.names()
        return Schema().bind(favorites=favorites)

    def appstruct(self):
        result = {'favorite': 'restart'}
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
