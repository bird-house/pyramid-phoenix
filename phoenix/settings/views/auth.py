from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from deform import Form
from deform import ValidationFailure

from phoenix.settings.views import SettingsView

import logging
logger = logging.getLogger(__name__)

class Auth(SettingsView):
    def __init__(self, request):
        super(Auth, self).__init__(request, name='settings_auth', title='Auth')
        self.settings = self.db.settings.find_one()
        if self.settings is None:
            self.settings = {}

    def breadcrumbs(self):
        breadcrumbs = super(Auth, self).breadcrumbs()
        breadcrumbs.append(dict(route_path=self.request.route_path(self.name), title=self.title))
        return breadcrumbs

    def generate_form(self):
        from phoenix.settings.schema import AuthSchema
        return Form(schema=AuthSchema(), buttons=('submit',), formid='deform')

    def process_form(self, form):
        try:
            controls = self.request.POST.items()
            appstruct = form.validate(controls)
        except ValidationFailure, e:
            logger.exception('validation of user form failed')
            return dict(title=self.title, form = e.render())
        except Exception, e:
            logger.exception('edit auth failed.')
            self.session.flash('Edit auth failed. %s' % (e), queue="danger")
        else:
            self.settings['auth'] = {}
            self.settings['auth']['protocol'] = list(appstruct.get('protocol'))
            self.db.settings.save(self.settings)

            # TODO: use events, config, settings, ... to update auth
            self.session.flash('Successfully updated Auth settings!', queue='success')
        return HTTPFound(location=self.request.route_path('settings_auth'))

    def appstruct(self):
        return self.settings.get('auth', {})

    @view_config(route_name='settings_auth', renderer='../templates/settings/auth.pt')
    def view(self):
        form = self.generate_form()
        if 'submit' in self.request.POST:
            return self.process_form(form)
        return dict(title=self.title, form=form.render(self.appstruct()))


