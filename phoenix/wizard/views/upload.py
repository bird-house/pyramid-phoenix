from pyramid.view import view_config
from pyramid.security import authenticated_userid

import colander

from phoenix.wizard.views import Wizard

class Schema(colander.Schema):
    url = colander.SchemaNode(
        colander.Set(),
        title="Filename",
        )

class Upload(Wizard):
    def __init__(self, request):
        super(Upload, self).__init__(
            request, name='wizard_upload',
            title="Upload files to local storage")

    def breadcrumbs(self):
        breadcrumbs = super(Upload, self).breadcrumbs()
        breadcrumbs.append(dict(route_path=self.request.route_path(self.name), title=self.title))
        return breadcrumbs

    def schema(self):
        return Schema().bind(request=self.request)

    def success(self, appstruct):
        super(Upload, self).success(appstruct)

    def next_success(self, appstruct):
        self.success(appstruct)
        return self.next('wizard_storage')

    @view_config(route_name='wizard_upload', renderer='../templates/wizard/upload.pt')
    def view(self):
        return super(Upload, self).view()
