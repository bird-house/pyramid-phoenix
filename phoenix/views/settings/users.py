from pyramid.view import view_config

from pyramid.httpexceptions import HTTPException, HTTPFound, HTTPNotFound
from deform import Form, Button
from deform import ValidationFailure

from phoenix.views.settings import SettingsView
from phoenix.grid import MyGrid

import logging
logger = logging.getLogger(__name__)

class Users(SettingsView):
    def __init__(self, request):
        super(Users, self).__init__(request, name='user_settings', title='Users')

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

    @view_config(route_name='remove_user')
    def remove(self):
        email = self.request.matchdict.get('email')
        if email is not None:
            self.userdb.remove(dict(email=email))
            self.session.flash('User %s removed' % (email), queue="info")
        return HTTPFound(location=self.request.route_url('user_settings'))

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

    def breadcrumbs(self):
        breadcrumbs = super(Users, self).breadcrumbs()
        breadcrumbs.append(dict(route_name='user_settings', title="Users"))
        return breadcrumbs

    @view_config(route_name='user_settings', renderer='phoenix:templates/settings/users.pt')
    def view(self):
        form = self.generate_form()
        if 'submit' in self.request.POST:
            return self.process_form(form)

        order = self.sort_order()
        user_items = list(self.userdb.find().sort(order.get('order'), order.get('order_dir')))
        grid = UsersGrid(
                self.request,
                user_items,
                ['name', 'email', 'openid', 'organisation', 'notes', 'activated', ''],
            )
        return dict(
            grid=grid,
            items=user_items,
            form=form.render())

class UsersGrid(MyGrid):
    def __init__(self, request, *args, **kwargs):
        super(UsersGrid, self).__init__(request, *args, **kwargs)
        self.column_formats['activated'] = self.activated_td
        self.column_formats[''] = self.action_td
        self.exclude_ordering = ['notes', '']

    def activated_td(self, col_num, i, item):
        from string import Template
        from webhelpers.html.builder import HTML

        icon_class = "icon-thumbs-down"
        if item.get('activated') == True:
            icon_class = "icon-thumbs-up"
        div = Template("""\
        <a class="activate" data-value="${email}" href="#"><i class="${icon_class}"></i></a>
        """)
        return HTML.td(HTML.literal(div.substitute({'email': item['email'], 'icon_class': icon_class} )))

    def action_td(self, col_num, i, item):
        buttongroup = []
        buttongroup.append( ("edit", item.get('email'), "icon-pencil", "Edit", "#"))
        buttongroup.append( ("remove", item.get('email'), "icon-trash", "Remove", 
                             self.request.route_url('remove_user', email=item.get('email'))) )
        return self.render_action_td(buttongroup)
