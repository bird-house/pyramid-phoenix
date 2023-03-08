from pyramid.view import view_config, view_defaults

from pyramid.httpexceptions import HTTPFound
from deform import Form, Button
from deform import ValidationFailure

from phoenix.views import MyView
from phoenix.security import check_csrf_token
from phoenix.security import Admin, User, Guest

import deform
import colander

import logging
LOGGER = logging.getLogger("PHOENIX")


class Schema(deform.schema.CSRFSchema):
    groups = ((Admin, 'Admin'), (User, 'User'), (Guest, 'Guest'))

    url = colander.SchemaNode(
        colander.String(),
        title='Service URL',
        description="Add URL of service (WPS). \
                    Example: http://localhost:5000/wps",
        default='http://localhost:5000/wps',
        validator=colander.url,
        widget=deform.widget.TextInputWidget())
    service_title = colander.SchemaNode(
        colander.String(),
        missing='',
        description="An optional service title. \
                    The title is used as a display name for the service. \
                    If a title is not provided it will be taken for the service metadata.")
    public = colander.SchemaNode(
        colander.Bool(),
        title="Public access?",
        description="Check this option if your service has no access restrictions.",
        default=False)
    group = colander.SchemaNode(
        colander.String(),
        validator=colander.OneOf([x[0] for x in choices]),
        widget=deform.widget.RadioChoiceWidget(values=groups, inline=True),
        title='Group',
        description='Select Group')


@view_defaults(permission='admin', layout='default')
class RegisterService(MyView):
    def __init__(self, request):
        super(RegisterService, self).__init__(
            request, name='register_service', title='Register New Service')

    def breadcrumbs(self):
        breadcrumbs = super(RegisterService, self).breadcrumbs()
        breadcrumbs.append(dict(route_path=self.request.route_path('settings'), title="Settings"))
        breadcrumbs.append(dict(route_path=self.request.route_path('services'), title="Services"))
        breadcrumbs.append(dict(route_path=self.request.route_path(self.name), title=self.title))
        return breadcrumbs

    def generate_form(self):
        return Form(Schema().bind(request=self.request), buttons=(Button(name='register', title='Register'),))

    def process_form(self, form):
        try:
            controls = list(self.request.POST.items())
            appstruct = form.validate(controls)
            url = appstruct.get('url')
            del appstruct['csrf_token']
            self.request.catalog.harvest(**appstruct)
            self.session.flash('Registered Service %s' % (url), queue="success")
        except ValidationFailure as e:
            return dict(title=self.title, form=e.render())
        except Exception as ex:
            LOGGER.exception('could not register service.')
            self.session.flash('Could not register Service {0}: {1}'.format(url, ex), queue="danger")
        return HTTPFound(location=self.request.route_path('services'))

    @view_config(route_name="register_service", renderer='phoenix:services/templates/services/service_register.pt')
    def view(self):
        form = self.generate_form()
        if 'register' in self.request.POST:
            check_csrf_token(self.request)
            return self.process_form(form)
        return dict(title=self.title, form=form.render())
