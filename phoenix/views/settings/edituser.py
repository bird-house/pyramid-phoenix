from pyramid.view import view_config

from pyramid.httpexceptions import HTTPFound
from deform import Form
from deform import ValidationFailure

from phoenix.views.settings import SettingsView

import logging
logger = logging.getLogger(__name__)

class EditUser(SettingsView):
    def __init__(self, request):
        self.email = request.matchdict.get('email')
        super(EditUser, self).__init__(request, name='settings_edit_user', title='Edit User')
       
    def breadcrumbs(self):
        breadcrumbs = super(EditUser, self).breadcrumbs()
        # TODO: fix breadcrumb generation
        breadcrumbs.append(dict(route_path=self.request.route_path('settings_users'), title="Users"))
        breadcrumbs.append(dict(route_path=self.request.route_path(self.name, email=self.email), title=self.title))
        return breadcrumbs

    def generate_form(self):
        from phoenix.schema.settings import UserSchema
        return Form(schema=UserSchema(), buttons=('submit',), formid='deform')

    def process_form(self, form):
        try:
            controls = self.request.POST.items()
            appstruct = form.validate(controls)
            user = self.get_user(self.email)
            for key in ['name', 'organisation', 'notes', 'group']:
                user[key] = appstruct.get(key)
            logger.debug('update user: email=%s, %s', self.email, user)
            self.db.users.update({'email':self.email}, user)
        except ValidationFailure, e:
            logger.exception('validation of user form failed')
            return dict(title=self.title, form = e.render())
        except Exception, e:
            logger.exception('edit user failed')
            self.session.flash('Edit user failed. %s' % (e), queue="error")
        return HTTPFound(location=self.request.route_path('settings_users'))

    def appstruct(self):
        return self.get_user(self.email)

    @view_config(route_name='settings_edit_user', renderer='phoenix:templates/settings/edit_user.pt')
    def view(self):
        form = self.generate_form()
        if 'submit' in self.request.POST:
            return self.process_form(form)

        return dict(title=self.title, form=form.render(self.appstruct()))
