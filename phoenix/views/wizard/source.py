from pyramid.view import view_config

from phoenix.views.wizard import Wizard

import colander
from deform.widget import RadioChoiceWidget

class ChooseSourceSchema(colander.MappingSchema):
    choices = [
        # TODO: enable csw again
        #('wizard_csw', "CSW Catalog Search"),
        ('wizard_esgf_search', "ESGF Files"),
        ('wizard_swift_login', "Swift Cloud")
        ]
    source = colander.SchemaNode(
        colander.String(),
        widget = RadioChoiceWidget(values = choices))

class ChooseSource(Wizard):
    def __init__(self, request):
        super(ChooseSource, self).__init__(
            request, name='wizard_source', title="Choose Source")
        self.description = self.wizard_state.get('wizard_complex_inputs')['identifier']
        
    def schema(self):
        return ChooseSourceSchema()

    def next_success(self, appstruct):
        self.success(appstruct)
        return self.next( appstruct.get('source') )
        
    @view_config(route_name='wizard_source', renderer='phoenix:templates/wizard/default.pt')
    def view(self):
        return super(ChooseSource, self).view()
    
