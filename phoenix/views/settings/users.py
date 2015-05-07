from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from phoenix.views.settings import SettingsView
from phoenix.grid import MyGrid

import logging
logger = logging.getLogger(__name__)

class Users(SettingsView):
    def __init__(self, request):
        super(Users, self).__init__(request, name='user_settings', title='Users')

    def breadcrumbs(self):
        breadcrumbs = super(Users, self).breadcrumbs()
        breadcrumbs.append(dict(route_path=self.request.route_path(self.name), title=self.title))
        return breadcrumbs

    def sort_order(self):
        """Determine what the current sort parameters are.
        """
        order = self.request.GET.get('order_col', 'last_login')
        order_dir = self.request.GET.get('order_dir', 'asc')
        order_dir = 1 if order_dir == 'asc' else -1
        return dict(order=order, order_dir=order_dir)   
        
    @view_config(route_name='remove_user')
    def remove(self):
        email = self.request.matchdict.get('email')
        if email is not None:
            self.userdb.remove(dict(email=email))
            self.session.flash('User %s removed' % (email), queue="info")
        return HTTPFound(location=self.request.route_path('user_settings'))

    @view_config(route_name='user_settings', renderer='phoenix:templates/settings/users.pt')
    def view(self):
        order = self.sort_order()
        user_items = list(self.userdb.find().sort(order.get('order'), order.get('order_dir')))
        grid = UsersGrid(
                self.request,
                user_items,
                ['name', 'email', 'openid', 'organisation', 'notes', 'group', 'last_login', ''],
            )
        return dict(grid=grid)

class UsersGrid(MyGrid):
    def __init__(self, request, *args, **kwargs):
        super(UsersGrid, self).__init__(request, *args, **kwargs)
        self.column_formats['last_login'] = self.last_login_td
        self.column_formats[''] = self.action_td
        self.exclude_ordering = self.columns

    def last_login_td(self, col_num, i, item):
        return self.render_time_ago_td(item.get('last_login'))

    def activated_td(self, col_num, i, item):
        return self.render_flag_td(item.get('activated'))

    def action_td(self, col_num, i, item):
        buttongroup = []
        buttongroup.append( ("edit", item.get('email'), "glyphicon glyphicon-pencil", "Edit",
                             self.request.route_path('settings_edit_user', email=item.get('email')), False))
        buttongroup.append( ("remove", item.get('email'), "glyphicon glyphicon-trash text-danger", "Remove", 
                             self.request.route_path('remove_user', email=item.get('email')),
                             False) )
        return self.render_action_td(buttongroup)
