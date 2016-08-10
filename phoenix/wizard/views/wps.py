from pyramid.view import view_config
import colander
import deform

from phoenix.catalog import WPS_TYPE
from phoenix.wizard.views import Wizard

import logging
logger = logging.getLogger(__name__)


class ChooseWPSSchema(colander.MappingSchema):
    @colander.deferred
    def deferred_validator(node, kw):
        wps_list = kw.get('wps_list', [])
        choices = []
        for wps in wps_list:
            choices.append(wps['service_name'])
        return colander.OneOf(choices)
    
    @colander.deferred
    def deferred_widget(node, kw):
        wps_list = kw.get('wps_list', [])
        choices = []
        for wps in wps_list:
            title = "{0} - {1}".format(wps['title'], wps['abstract'])
            choices.append((wps['service_name'], title))
        return deform.widget.RadioChoiceWidget(values = choices)
    
    identifier = colander.SchemaNode(
        colander.String(),
        title="Web Processing Service",
        validator=deferred_validator,
        widget=deferred_widget
        )


class ChooseWPS(Wizard):
    def __init__(self, request):
        super(ChooseWPS, self).__init__(request, name='wizard_wps', title='Choose a Web Processing Service')

    def breadcrumbs(self):
        breadcrumbs = super(ChooseWPS, self).breadcrumbs()
        breadcrumbs.append(dict(route_path=self.request.route_path(self.name), title=self.title))
        return breadcrumbs

    def schema(self):
        wps_list = []
        for service in self.request.catalog.get_services(service_type=WPS_TYPE):
            wps_list.append({'title': service.title,
                             'abstract': service.abstract,
                             'service_name': service.service_name})
        return ChooseWPSSchema().bind(wps_list=wps_list)

    def next_success(self, appstruct):
        self.success(appstruct)
        return self.next('wizard_process')

    @view_config(route_name='wizard_wps', renderer='../templates/wizard/default.pt')
    def view(self):
        return super(ChooseWPS, self).view()
    
