from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound
from deform import Form
from deform import ValidationFailure

from phoenix.views import MyView
from phoenix.events import SettingsChanged
from phoenix.utils import skip_csrf_token
# TODO: move settings to processes
from phoenix.settings.schema import ProcessesSchema
from phoenix.security import check_csrf_token

import logging
LOGGER = logging.getLogger("PHOENIX")


@view_defaults(permission='admin', layout='default')
class Processes(MyView):
    def __init__(self, request):
        super(Processes, self).__init__(request, name='settings_processes', title='Processes')
        self.collection = self.request.db.settings

    def breadcrumbs(self):
        breadcrumbs = super(Processes, self).breadcrumbs()
        breadcrumbs.append(dict(route_path=self.request.route_path('settings'), title="Settings"))
        breadcrumbs.append(dict(route_path=self.request.route_path(self.name), title=self.title))
        return breadcrumbs

    def generate_form(self):
        processes = {}  # ProcessesActions(self.context, self.request).list_processes()
        return Form(schema=ProcessesSchema().bind(request=self.request, processes=processes),
                    buttons=('submit',), formid='deform')

    def process_form(self, form):
        try:
            controls = list(self.request.POST.items())
            appstruct = skip_csrf_token(form.validate(controls))
        except ValidationFailure as e:
            return dict(title=self.title, form=e.render())
        except Exception:
            self.session.flash("<strong>Error:</strong> Could not update settings.", queue="danger")
        else:
            settings = self.collection.find_one() or {}
            settings.update(dict(pinned_processes=list(appstruct['pinned_processes'])))
            self.collection.save(settings)
            self.request.registry.notify(SettingsChanged(self.request, appstruct))
            self.session.flash('Successfully updated settings!', queue='success')
        return HTTPFound(location=self.request.route_path('settings_processes'))

    def appstruct(self):
        appstruct = self.collection.find_one() or {}
        return skip_csrf_token(appstruct)

    @view_config(route_name='settings_processes', renderer='phoenix:settings/templates/settings/processes.pt')
    def view(self):
        form = self.generate_form()
        if 'submit' in self.request.POST:
            check_csrf_token(self.request)
            return self.process_form(form)
        return dict(title=self.title, form=form.render(self.appstruct()))
