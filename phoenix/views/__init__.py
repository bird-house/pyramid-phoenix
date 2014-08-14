import logging
logger = logging.getLogger(__name__)

class MyView(object):
    def __init__(self, request, title, description=None):
        self.request = request
        self.session = self.request.session
        self.title = title
        self.description = description
        # db access
        self.userdb = self.request.db.users

        # set breadcrumbs
        for item in self.breadcrumbs():
            lm = self.request.layout_manager
            lm.layout.add_breadcrumb(
                route_name=item.get('route_name'),
                title=item.get('title'))

    def user_email(self):
        from pyramid.security import authenticated_userid
        return authenticated_userid(self.request)

    def get_user(self, email=None):
        if email is None:
            email = self.user_email()
        return self.userdb.find_one(dict(email=email))

    def breadcrumbs(self):
        return [dict(route_name="home", title="Home")]

