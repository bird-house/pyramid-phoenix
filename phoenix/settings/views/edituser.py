from pyramid.view import view_config

from pyramid.httpexceptions import HTTPFound
from deform import Form
from deform import ValidationFailure

from phoenix.settings.views import SettingsView

import logging
logger = logging.getLogger(__name__)

class EditUser(SettingsView):
    def __init__(self, request):
        # TODO: fix handling of userid
        self.userid = request.matchdict.get('userid')
        super(EditUser, self).__init__(request, name='settings_edit_user', title='Edit User')
       
    def breadcrumbs(self):
        breadcrumbs = super(EditUser, self).breadcrumbs()
        # TODO: fix breadcrumb generation
        breadcrumbs.append(dict(route_path=self.request.route_path('settings_users'), title="Users"))
        breadcrumbs.append(dict(route_path=self.request.route_path(self.name, userid=self.userid), title=self.title))
        return breadcrumbs

    def generate_form(self):
        from phoenix.settings.schema import EditUserSchema
        return Form(schema=EditUserSchema(), buttons=('submit',), formid='deform')

    def process_form(self, form):
        try:
            controls = self.request.POST.items()
            appstruct = form.validate(controls)
            user = self.userdb.find_one(dict(identifier=self.userid))
            for key in ['name', 'email', 'organisation', 'notes', 'group']:
                user[key] = appstruct.get(key)
            self.db.users.update({'identifier':self.userid}, user)
        except ValidationFailure, e:
            logger.exception('validation of user form failed')
            return dict(title=self.title, form = e.render())
        except Exception, e:
            logger.exception('edit user failed')
            self.session.flash('Edit user failed. %s' % (e), queue="danger")
        return HTTPFound(location=self.request.route_path('settings_users'))

    def appstruct(self):
        return self.userdb.find_one(dict(identifier=self.userid))

    @view_config(route_name='settings_edit_user', renderer='../templates/settings/edit_user.pt')
    def view(self):
        form = self.generate_form()
        if 'submit' in self.request.POST:
            return self.process_form(form)

        return dict(title=self.title, form=form.render(self.appstruct()))
