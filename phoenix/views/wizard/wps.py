from pyramid.view import view_config
import colander
import deform

from phoenix.views.wizard import Wizard

class ChooseWPSSchema(colander.MappingSchema):
    @colander.deferred
    def deferred_wps_list_widget(node, kw):
        wps_list = kw.get('wps_list', [])
        choices = []
        for wps in wps_list:
            title = "%s (%s) [%s]" % (wps.get('title'), wps.get('abstract'), wps.get('source'))
            choices.append((wps.get('source'), title))
        return deform.widget.RadioChoiceWidget(values = choices)
    
    url = colander.SchemaNode(
        colander.String(),
        title = 'WPS service',
        description = "Select WPS",
        widget = deferred_wps_list_widget
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
        from phoenix.models import get_wps_list
        return ChooseWPSSchema().bind(wps_list = get_wps_list(self.request))

    def next_success(self, appstruct):
        self.success(appstruct)
        return self.next('wizard_process')

    @view_config(route_name='wizard_wps', renderer='phoenix:templates/wizard/default.pt')
    def view(self):
        return super(ChooseWPS, self).view()
    
