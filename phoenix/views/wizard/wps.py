from pyramid.view import view_config

from phoenix.views.wizard import Wizard

class ChooseWPS(Wizard):
    def __init__(self, request):
        super(ChooseWPS, self).__init__(request, name='wizard_wps', title='WPS')
        self.description = "Choose Web Processing Service"

    def breadcrumbs(self):
        breadcrumbs = super(ChooseWPS, self).breadcrumbs()
        breadcrumbs.append(dict(route_path=self.request.route_path(self.name), title=self.title))
        return breadcrumbs

    def schema(self):
        from phoenix.schema import ChooseWPSSchema
        from phoenix import models
        return ChooseWPSSchema().bind(wps_list = models.get_wps_list(self.request))

    def next_success(self, appstruct):
        self.success(appstruct)
        return self.next('wizard_process')

    @view_config(route_name='wizard_wps', renderer='phoenix:templates/wizard/default.pt')
    def view(self):
        return super(ChooseWPS, self).view()
    
