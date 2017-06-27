import colander
import deform
from deform.widget import RadioChoiceWidget

from pyramid.view import view_config

from owslib.wps import WebProcessingService

from phoenix.esgf.search import query_params_from_appstruct
from phoenix.esgf.metadata import process_constraints
from phoenix.wizard.views import Wizard

SOURCE_TYPES = {
    'wizard_esgf_search': "Earth System Grid (ESGF)",
    'wizard_threddsservice': "Thredds Catalog Service",
    'wizard_solr': "Birdhouse Solr Search"
}


def includeme(config):
    config.add_route('wizard_source', '/wizard/source')
    config.add_view('phoenix.wizard.views.source.ChooseSource',
                    route_name='wizard_source',
                    attr='view',
                    renderer='../templates/wizard/default.pt')


class SourceSchemaNode(colander.SchemaNode):
    schema_type = colander.String
    widget = None

    def after_bind(self, node, kw):
        values = SOURCE_TYPES.items()
        if not kw['request'].solr_activated:
            values.remove(('wizard_solr', SOURCE_TYPES['wizard_solr']))
        self.widget = RadioChoiceWidget(values=values)


class Schema(deform.schema.CSRFSchema):
    source = SourceSchemaNode()


class ChooseSource(Wizard):
    def __init__(self, request):
        super(ChooseSource, self).__init__(
            request, name='wizard_source', title="Choose Data Source")
        self.wps = WebProcessingService(
            url=request.route_url('owsproxy', service_name=self.wizard_state.get('wizard_wps')['identifier']),
            verify=False, skip_caps=True)
        self.process = self.wps.describeprocess(self.wizard_state.get('wizard_process')['identifier'])
        for data_input in self.process.dataInputs:
            if data_input.identifier == self.wizard_state.get('wizard_complex_inputs')['identifier']:
                self.title = "Choose Data Source for %s" % data_input.title
                break

    def breadcrumbs(self):
        breadcrumbs = super(ChooseSource, self).breadcrumbs()
        breadcrumbs.append(dict(route_path=self.request.route_path(self.name), title=self.title))
        return breadcrumbs

    def schema(self):
        return Schema().bind(request=self.request)

    def next_success(self, appstruct):
        self.success(appstruct)
        # TODO: that is a dirty way to init esgf search
        if appstruct.get('source') == 'wizard_esgf_search':
            defaults = dict(constraints=process_constraints(self.process))
            query = query_params_from_appstruct(self.wizard_state.get('wizard_esgf_search'), defaults)
            if not self.request.cert_ok:
                msg = """<strong>Error:</strong> You are not allowed to access ESGF data.
                Please <a href="{}" class="alert-link">update</a> your ESGF credentials."""
                callback = self.request.current_route_path()
                self.session.flash(
                    msg.format(self.request.route_path('esgflogon', _query=[('callback', callback)])),
                    queue='danger')
                return self.next(self.name)
        else:
            query = None
        return self.next(appstruct.get('source'), query=query)

    def view(self):
        return super(ChooseSource, self).view()
