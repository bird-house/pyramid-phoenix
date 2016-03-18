from pyramid.view import view_config
import colander
import deform

from phoenix.wizard.views import Wizard

class Schema(colander.MappingSchema):
    url = colander.SchemaNode(
        colander.String(),
        title = "Filename",
        )

class Storage(Wizard):
    def __init__(self, request):
        super(Storage, self).__init__(
            request, name='wizard_storage',
            title="Select file from local storage")

    def breadcrumbs(self):
        breadcrumbs = super(Storage, self).breadcrumbs()
        breadcrumbs.append(dict(route_path=self.request.route_path(self.name), title=self.title))
        return breadcrumbs

    def schema(self):
        return Schema()

    def success(self, appstruct):
        super(Storage, self).success(appstruct)

    def next_success(self, appstruct):
        self.success(appstruct)
        return self.next('wizard_done')

    @view_config(route_name='wizard_storage', renderer='../templates/wizard/default.pt')
    def view(self):
        return super(Storage, self).view()

