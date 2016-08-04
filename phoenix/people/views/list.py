from pyramid.view import view_config, view_defaults

from phoenix.views import MyView
from phoenix.security import Admin, User, Guest
from phoenix.grid import CustomGrid

import logging
logger = logging.getLogger(__name__)


@view_defaults(permission='admin', layout='default')
class People(MyView):
    def __init__(self, request):
        super(People, self).__init__(request, name='people', title='')
        self.collection = self.request.db.users

    @view_config(route_name='people', renderer='../templates/people/list.pt')
    def view(self):
        user_items = list(self.collection.find().sort('last_login', -1))
        grid = PeopleGrid(
                self.request,
                user_items,
                ['name', 'userid', 'email', 'organisation', 'notes', 'group', 'last_login', ''],
            )
        return dict(grid=grid)


class PeopleGrid(CustomGrid):
    def __init__(self, request, *args, **kwargs):
        super(PeopleGrid, self).__init__(request, *args, **kwargs)
        self.column_formats['userid'] = self.label_td('login_id')
        self.column_formats['group'] = self.group_td
        self.column_formats['last_login'] = self.time_ago_td('last_login')
        self.column_formats[''] = self.buttongroup_td
        self.exclude_ordering = self.columns

    def group_td(self, col_num, i, item):
        from webhelpers2.html.builder import HTML
        group = item.get('group')
        label = "???"
        if group == Admin:
            label = "Admin"
        elif group == User:
            label = "User"
        elif group == Guest:
            label = "Guest"
        return HTML.td(label)

    def buttongroup_td(self, col_num, i, item):
        from phoenix.utils import ActionButton
        buttons = list()
        buttons.append(ActionButton('edit', css_class="btn btn-success", icon="fa fa-pencil",
                                    href=self.request.route_path('profile', userid=item.get('identifier'),
                                                                 tab='account')))
        buttons.append(ActionButton('remove', css_class="btn btn-danger", icon="fa fa-trash",
                                    href=self.request.route_path('delete_user', userid=item.get('identifier'))))
        return self.render_buttongroup_td(buttons=buttons)
    

