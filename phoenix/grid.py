from webhelpers.html.builder import HTML
from webhelpers.html.grid import ObjectGrid

class UsersGrid(ObjectGrid):
    """A generated table for the todo list that supports ordering of
    the task name and due date columns. We also customize the init so
    that we accept the selected_tag and user_tz.
    """

    def __init__(self, request, *args, **kwargs):
        self.request = request
        if 'url' not in kwargs:
            kwargs['url'] = request.current_route_url
        super(UsersGrid, self).__init__(*args, **kwargs)

