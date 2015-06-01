from pyramid.view import view_config

from pyramid.httpexceptions import HTTPFound
from deform import Form, Button
from deform import ValidationFailure

from . import SettingsView

import logging
logger = logging.getLogger(__name__)

class AddService(SettingsView):
    def __init__(self, request):
        super(AddService, self).__init__(
            request, name='settings_add_service', title='Add Service')
        self.csw = self.request.csw
        self.description = "Add OGC service to catalog."

    def breadcrumbs(self):
        breadcrumbs = super(AddService, self).breadcrumbs()
        # TODO: fix breadcrumb
        breadcrumbs.append(dict(route_path=self.request.route_path('settings_catalog'), title="Catalog"))
        breadcrumbs.append(dict(route_path=self.request.route_path(self.name), title=self.title))
        return breadcrumbs
        
    def generate_form(self):
        from phoenix.schema import CatalogAddServiceSchema
        schema = CatalogAddServiceSchema()
        return Form(schema, buttons=(Button(name='add_service', title='Add Service'),), formid='deform')

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
        return HTTPFound(location=self.request.route_url('settings_catalog'))

    @view_config(route_name="settings_add_service", renderer='phoenix:templates/settings/add_service.pt')
    def view(self):
        form = self.generate_form()
        if 'add_service' in self.request.POST:
            return self.process_form(form)
        return dict(title=self.title, form=form.render())


