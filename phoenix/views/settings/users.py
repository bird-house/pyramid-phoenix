from pyramid.view import view_config

from pyramid.httpexceptions import HTTPException, HTTPFound, HTTPNotFound
from deform import Form, Button
from deform import ValidationFailure

from phoenix.views.settings import SettingsView

import logging
logger = logging.getLogger(__name__)

class Users(SettingsView):
    def __init__(self, request):
        super(Users, self).__init__(request, 'Users')

    def sort_order(self):
        """Determine what the current sort parameters are.
        """
        order = self.request.GET.get('order_col', 'activated')
        order_dir = self.request.GET.get('order_dir', 'asc')
        order_dir = 1 if order_dir == 'asc' else -1
        return dict(order=order, order_dir=order_dir)   
        
    def generate_form(self, formid="deform"):
        from phoenix.schema import UserSchema
        schema = UserSchema().bind()
        return Form(
            schema,
            buttons=('submit',),
            formid=formid)

    def process_form(self, form):
        try:
            controls = self.request.POST.items()
            appstruct = form.validate(controls)
            # TODO: fix update user ... email is readonly
            user = self.get_user(appstruct.get('email'))
            for key in ['name', 'openid', 'organisation', 'notes']:
                user[key] = appstruct.get(key)
            self.userdb.update({'email':self.user_email()}, user)
        except ValidationFailure, e:
            logger.exception('validation of user form failed')
            return dict(form = e.render())
        except Exception, e:
            logger.exception('edit user failed')
            self.session.flash('Edit user failed. %s' % (e), queue="error")
        return HTTPFound(location=self.request.route_url('user_settings'))

    @view_config(route_name='delete_user', renderer='json')
    def delete(self):
        email = self.request.matchdict.get('email')
        if email is not None:
            self.userdb.remove(dict(email=email))
        return {}

    @view_config(route_name='activate_user', renderer='json')
    def activate(self):
        email = self.request.matchdict.get('email')
        if email is not None:
            user = self.userdb.find_one({'email':email})
            user['activated'] = not user.get('activated', True)
            self.userdb.update({'email':email}, user)
        return {}

    @view_config(route_name='edit_user', renderer='json')
    def edit(self):
        email = self.request.matchdict.get('email')
        user = None
        if email is not None:
            user = self.userdb.find_one({'email':email})
        if user is None:
            user = dict(email=email)
        return user

    @view_config(route_name='user_settings', renderer='phoenix:templates/settings/users.pt')
    def view(self):
        form = self.generate_form()
        if 'submit' in self.request.POST:
            return self.process_form(form)

        from phoenix.grid import UsersGrid
        order = self.sort_order()
        user_items = list(self.userdb.find().sort(order.get('order'), order.get('order_dir')))
        logger.debug('user_items: %s', user_items)
        grid = UsersGrid(
                self.request,
                user_items,
                ['name', 'email', 'openid', 'organisation', 'notes', 'activated', ''],
            )
        return dict(
            grid=grid,
            items=user_items,
            form=form.render())

