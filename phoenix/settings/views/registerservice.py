from pyramid.view import view_config

from pyramid.httpexceptions import HTTPFound
from deform import Form, Button
from deform import ValidationFailure

from . import SettingsView

import logging
logger = logging.getLogger(__name__)

class RegisterService(SettingsView):
    def __init__(self, request):
        super(RegisterService, self).__init__(
            request, name='settings_register_service', title='Register New Service')
        self.csw = self.request.csw
        self.description = "Add OGC service to catalog."

    def breadcrumbs(self):
        breadcrumbs = super(RegisterService, self).breadcrumbs()
        # TODO: fix breadcrumb
        breadcrumbs.append(dict(route_path=self.request.route_path('settings_services'), title="Services"))
        breadcrumbs.append(dict(route_path=self.request.route_path(self.name), title=self.title))
        return breadcrumbs
        
    def generate_form(self):
        from phoenix.schema import CatalogAddServiceSchema
        schema = CatalogAddServiceSchema()
        return Form(schema, buttons=(Button(name='register', title='Register'),))

    def process_form(self, form):
        try:
            controls = self.request.POST.items()
            appstruct = form.validate(controls)
            url = appstruct.get('url')
            self.csw.harvest(
                source=url,
                resourcetype=appstruct.get('resource_type'))
            self.session.flash('Added WPS %s' % (url), queue="success")
        except ValidationFailure, e:
            logger.exception('validation of catalog form failed')
            return dict(title=self.title, form = e.render())
        except Exception, e:
            logger.exception('could not harvest wps.')
            self.session.flash('Could not add WPS %s. %s' % (url, e), queue="danger")
        return HTTPFound(location=self.request.route_path('settings_services'))

    @view_config(route_name="settings_register_service", renderer='../templates/settings/service_register.pt')
    def view(self):
        form = self.generate_form()
        if 'register' in self.request.POST:
            return self.process_form(form)
        return dict(title=self.title, form=form.render())


