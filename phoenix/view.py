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

    def user_email(self):
        from pyramid.security import authenticated_userid
        return authenticated_userid(self.request)

    def get_user(self, email=None):
        if email is None:
            email = self.user_email()
        return self.userdb.find_one(dict(email=email))
