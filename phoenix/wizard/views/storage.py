import glob
import os

from pyramid.view import view_config
from pyramid.security import authenticated_userid
import colander
import deform

from phoenix.wizard.views import Wizard


@colander.deferred
def deferred_checkbox_widget(node, kw):
    request = kw.get('request')
    folder = authenticated_userid(request)
    listing = [os.path.basename(entry) for entry in glob.glob(os.path.join(request.storage.base_path, folder, '*'))]

    choices = []
    for entry in listing:
        filename = os.path.join(folder, entry)
        if request.storage.exists(filename):
            choices.append( (request.storage.url(filename), entry) )
    return deform.widget.CheckboxChoiceWidget(values=choices)
    
class Schema(colander.Schema):
    url = colander.SchemaNode(
        colander.Set(),
        title="Filename",
        widget=deferred_checkbox_widget,
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
        return Schema().bind(request=self.request)

    def success(self, appstruct):
        super(Storage, self).success(appstruct)

    def next_success(self, appstruct):
        self.success(appstruct)
        return self.next('wizard_done')

    @view_config(route_name='wizard_storage', renderer='../templates/wizard/default.pt')
    def view(self):
        return super(Storage, self).view()

