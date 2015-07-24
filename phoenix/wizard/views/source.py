from pyramid.view import view_config

from phoenix.wizard.views import Wizard

import colander
from deform.widget import RadioChoiceWidget

class Schema(colander.MappingSchema):
    choices = [
        ('wizard_esgf_search', "Earth System Grid (ESGF)"),
        ('wizard_swift_login', "Swift Cloud"),
        ('wizard_threddsservice', "Thredds Catalog Service"),
        ('wizard_solr', "Birdhouse Solr Search")
        ]
    source = colander.SchemaNode(
        colander.String(),
        widget = RadioChoiceWidget(values = choices))

class ChooseSource(Wizard):
    def __init__(self, request):
        super(ChooseSource, self).__init__(
            request, name='wizard_source', title="Choose Data Source")
        self.description = self.wizard_state.get('wizard_complex_inputs')['identifier']

    def breadcrumbs(self):
        breadcrumbs = super(ChooseSource, self).breadcrumbs()
        breadcrumbs.append(dict(route_path=self.request.route_path(self.name), title=self.title))
        return breadcrumbs
        
    def schema(self):
        return Schema()

    def next_success(self, appstruct):
        self.success(appstruct)
        return self.next( appstruct.get('source') )
        
    @view_config(route_name='wizard_source', renderer='../templates/wizard/default.pt')
    def view(self):
        return super(ChooseSource, self).view()
    
