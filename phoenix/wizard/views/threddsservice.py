from pyramid.view import view_config
import colander
import deform

from phoenix.catalog import THREDDS_TYPE
from phoenix.wizard.views import Wizard


def includeme(config):
    config.add_route('wizard_threddsservice', '/wizard/threddsservice')
    config.add_view('phoenix.wizard.views.threddsservice.ThreddsService',
                    route_name='wizard_threddsservice',
                    attr='view',
                    renderer='../templates/wizard/default.pt')
    config.add_route('wizard_threddsbrowser', '/wizard/threddsbrowser')
    config.add_view('phoenix.wizard.views.threddsbrowser.ThreddsBrowser',
                    route_name='wizard_threddsbrowser',
                    attr='view',
                    renderer='../templates/wizard/threddsbrowser.pt')


@colander.deferred
def deferred_widget(node, kw):
    thredds_list = kw.get('thredds_list', [])

    choices = []
    for tds in thredds_list:
        description = "{0.title} - {0.source}".format(tds)
        choices.append((tds.source, description))
    return deform.widget.RadioChoiceWidget(values=choices)


class Schema(deform.schema.CSRFSchema):
    url = colander.SchemaNode(
        colander.String(),
        title="Thredds Service",
        widget=deferred_widget)


class ThreddsService(Wizard):
    def __init__(self, request):
        super(ThreddsService, self).__init__(
            request, name='wizard_threddsservice',
            title="Select Thredds Service")

    def breadcrumbs(self):
        breadcrumbs = super(ThreddsService, self).breadcrumbs()
        breadcrumbs.append(dict(route_path=self.request.route_path(self.name), title=self.title))
        return breadcrumbs

    def schema(self):
        return Schema().bind(
            request=self.request,
            thredds_list=self.request.catalog.get_services(service_type=THREDDS_TYPE))

    def success(self, appstruct):
        super(ThreddsService, self).success(appstruct)

    def next_success(self, appstruct):
        self.success(appstruct)
        return self.next('wizard_threddsbrowser')

    def view(self):
        return super(ThreddsService, self).view()
