from pyramid.view import view_config
import colander
import deform

from phoenix.wizard.views import Wizard
from phoenix.catalog import catalog_factory

@colander.deferred
def deferred_widget(node, kw):
    thredds_list = kw.get('thredds_list', [])

    choices = []
    for tds in thredds_list:
        description = "{0.title} - {0.source}".format(tds)
        choices.append( (tds.source, description) )
    return deform.widget.RadioChoiceWidget(values = choices)

class Schema(colander.MappingSchema):
    url = colander.SchemaNode(
        colander.String(),
        title = "Thredds Service",
        widget = deferred_widget)

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
        catalog = catalog_factory(self.request.registry)
        return Schema().bind(thredds_list=catalog.get_thredds_list())

    def success(self, appstruct):
        super(ThreddsService, self).success(appstruct)

    def next_success(self, appstruct):
        self.success(appstruct)
        return self.next('wizard_threddsbrowser')

    @view_config(route_name='wizard_threddsservice', renderer='../templates/wizard/default.pt')
    def view(self):
        return super(ThreddsService, self).view()
