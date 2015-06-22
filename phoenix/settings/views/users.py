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
        # TODO: fix handling of userids
        userid = self.request.matchdict.get('userid')
        if userid is not None:
            self.userdb.remove(dict(identifier=userid))
            self.session.flash('User removed', queue="info")
        return HTTPFound(location=self.request.route_path(self.name))

    @view_config(route_name='settings_users', renderer='../templates/settings/users.pt')
    def view(self):
        user_items = list(self.userdb.find().sort('last_login', -1))
        grid = UsersGrid(
                self.request,
                user_items,
                ['name', 'userid', 'organisation', 'notes', 'group', 'last_login', ''],
            )
        return dict(grid=grid)

class UsersGrid(MyGrid):
    def __init__(self, request, *args, **kwargs):
        super(UsersGrid, self).__init__(request, *args, **kwargs)
        self.column_formats['userid'] = self.userid_td
        self.column_formats['group'] = self.group_td
        self.column_formats['last_login'] = self.last_login_td
        self.column_formats[''] = self.action_td
        self.exclude_ordering = self.columns

    def userid_td(self, col_num, i, item):
        return self.render_label_td(item.get('userid'))

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
        buttongroup.append( ("edit", item.get('identifier'), "glyphicon glyphicon-pencil", "Edit",
                             self.request.route_path('settings_edit_user', userid=item.get('identifier')), False))
        buttongroup.append( ("remove", item.get('userid'), "glyphicon glyphicon-trash text-danger", "Remove", 
                             self.request.route_path('remove_user', userid=item.get('identifier')),
                             False) )
        return self.render_action_td(buttongroup)
