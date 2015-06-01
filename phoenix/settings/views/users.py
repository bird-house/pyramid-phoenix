from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from . import SettingsView
from phoenix.grid import MyGrid
from phoenix.security import Admin, User, Guest

import logging
logger = logging.getLogger(__name__)

class Users(SettingsView):
    def __init__(self, request):
        super(Users, self).__init__(request, name='settings_users', title='Users')

    def breadcrumbs(self):
        breadcrumbs = super(Users, self).breadcrumbs()
        breadcrumbs.append(dict(route_path=self.request.route_path(self.name), title=self.title))
        return breadcrumbs

    @view_config(route_name='remove_user')
    def remove(self):
        email = self.request.matchdict.get('email')
        if email is not None:
            self.userdb.remove(dict(email=email))
            self.session.flash('User %s removed' % (email), queue="info")
        return HTTPFound(location=self.request.route_path(self.name))

    @view_config(route_name='settings_users', renderer='phoenix:templates/settings/users.pt')
    def view(self):
        user_items = list(self.userdb.find().sort('last_login', -1))
        grid = UsersGrid(
                self.request,
                user_items,
                ['name', 'email', 'organisation', 'notes', 'group', 'last_login', ''],
            )
        return dict(grid=grid)

class UsersGrid(MyGrid):
    def __init__(self, request, *args, **kwargs):
        super(UsersGrid, self).__init__(request, *args, **kwargs)
        self.column_formats['group'] = self.group_td
        self.column_formats['last_login'] = self.last_login_td
        self.column_formats[''] = self.action_td
        self.exclude_ordering = self.columns

    def last_login_td(self, col_num, i, item):
        return self.render_time_ago_td(item.get('last_login'))

    def group_td(self, col_num, i, item):
        group = item.get('group')
        label = "???"
        if group == Admin:
            label = "Admin"
        elif group == User:
            label = "User"
        elif group == Guest:
            label = "Guest"
        return self.render_label_td(label)

    def action_td(self, col_num, i, item):
        buttongroup = []
        buttongroup.append( ("edit", item.get('email'), "glyphicon glyphicon-pencil", "Edit",
                             self.request.route_path('settings_edit_user', email=item.get('email')), False))
        buttongroup.append( ("remove", item.get('email'), "glyphicon glyphicon-trash text-danger", "Remove", 
                             self.request.route_path('remove_user', email=item.get('email')),
                             False) )
        return self.render_action_td(buttongroup)
