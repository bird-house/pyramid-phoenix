from pyramid.view import view_config
import colander
import deform

from phoenix.utils import get_wps_list
from phoenix.wizard.views import Wizard

class ChooseWPSSchema(colander.MappingSchema):
    @colander.deferred
    def deferred_validator(node, kw):
        wps_list = kw.get('wps_list', [])
        choices = []
        for wps in wps_list:
            choices.append(wps.identifier)
        return colander.OneOf(choices)
    
    @colander.deferred
    def deferred_widget(node, kw):
        wps_list = kw.get('wps_list', [])
        choices = []
        for wps in wps_list:
            title = "{0.title} - {0.abstract}".format(wps)
            choices.append((wps.identifier, title))
        return deform.widget.RadioChoiceWidget(values = choices)
    
    identifier = colander.SchemaNode(
        colander.String(),
        title = 'Choose a Web Processing Service',
        validator = deferred_validator,
        widget = deferred_widget
        )

class ChooseWPS(Wizard):
    def __init__(self, request):
        super(ChooseWPS, self).__init__(request, name='wizard_wps', title='WPS')
        self.description = "Choose Web Processing Service"

    def breadcrumbs(self):
        breadcrumbs = super(ChooseWPS, self).breadcrumbs()
        breadcrumbs.append(dict(route_path=self.request.route_path(self.name), title=self.title))
        return breadcrumbs

    def schema(self):
        return ChooseWPSSchema().bind(wps_list = get_wps_list(self.request))

    def next_success(self, appstruct):
        self.success(appstruct)
        return self.next('wizard_process')

    @view_config(route_name='wizard_wps', renderer='../templates/wizard/default.pt')
    def view(self):
        return super(ChooseWPS, self).view()
    
