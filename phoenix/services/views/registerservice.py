from pyramid.view import view_config

from pyramid.httpexceptions import HTTPFound
from deform import Form, Button
from deform import ValidationFailure

from phoenix.catalog import THREDDS_TYPE
from phoenix.settings.views import SettingsView

import deform
import colander

import logging
logger = logging.getLogger(__name__)

class Schema(colander.MappingSchema):
    service_types = [
        ('http://www.opengis.net/wps/1.0.0', "Web Processing Service"),
        (THREDDS_TYPE, "Thredds Catalog")]
    
    url = colander.SchemaNode(
        colander.String(),
        title = 'Service URL',
        description = 'Add URL of service (WPS, Thredds, ...). Example: http://localhost:8091/wps, http://localhost/thredds/catalog.xml',
        default = 'http://localhost:8091/wps',
        validator = colander.url,
        widget = deform.widget.TextInputWidget())
    service_name = colander.SchemaNode(
        colander.String(),
        missing = '',
        description = "An optional service name.")
    service_type = colander.SchemaNode(
        colander.String(),
        default = 'http://www.opengis.net/wps/1.0.0',
        widget = deform.widget.RadioChoiceWidget(values=service_types))

class RegisterService(SettingsView):
    def __init__(self, request):
        super(RegisterService, self).__init__(
            request, name='register_service', title='Register New Service')
       
    def breadcrumbs(self):
        breadcrumbs = super(RegisterService, self).breadcrumbs()
        breadcrumbs.append(dict(route_path=self.request.route_path('services'), title="Services"))
        breadcrumbs.append(dict(route_path=self.request.route_path(self.name), title=self.title))
        return breadcrumbs
    
    def generate_form(self):
        return Form(Schema(), buttons=(Button(name='register', title='Register'),))

    def process_form(self, form):
        try:
            controls = self.request.POST.items()
            appstruct = form.validate(controls)
            url = appstruct.get('url')
            self.request.catalog.harvest(**appstruct)
            self.session.flash('Registered Service %s' % (url), queue="success")
        except ValidationFailure, e:
            return dict(title=self.title, form = e.render())
        except Exception, ex:
            logger.exception('could not register service.')
            self.session.flash('Could not register Service {0}: {1}'.format(url, ex), queue="danger")
        return HTTPFound(location=self.request.route_path('services'))

    @view_config(route_name="register_service", renderer='../templates/services/service_register.pt')
    def view(self):
        form = self.generate_form()
        if 'register' in self.request.POST:
            return self.process_form(form)
        return dict(title=self.title, form=form.render())


