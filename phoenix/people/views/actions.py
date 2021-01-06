from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.security import authenticated_userid

from phoenix.oauth2 import oauth2_client_factory


class Actions(object):
    def __init__(self, request):
        self.request = request
        self.session = request.session
        # settings = request.registry.settings
        self.collection = self.request.db.users
        self.userid = self.request.matchdict.get('userid', authenticated_userid(self.request))

    @view_config(route_name='refresh_token', permission='submit')
    def refresh_token(self):
        try:
            client = oauth2_client_factory(self.request.registry)
            client.refresh_token(userid=self.userid)
        except Exception:
            self.session.flash('Could not refresh token.', queue="danger")
        else:
            self.session.flash('Token was updated.', queue="success")
        return HTTPFound(location=self.request.route_path('profile', userid=self.userid, tab='token'))

    @view_config(route_name='delete_user', permission='admin')
    def delete_user(self):
        if self.request.registry.settings.get("phoenix.local_user_management", "true").lower() != "true":
            return HTTPNotFound()
        if self.userid:
            self.collection.remove(dict(identifier=self.userid))
            self.session.flash('User removed', queue="info")
        return HTTPFound(location=self.request.route_path('people'))


def includeme(config):
    """ Pyramid includeme hook.
    :param config: app config
    :type config: :class:`pyramid.config.Configurator`
    """
    config.add_route('refresh_token', 'people/token')
    config.add_route('delete_user', 'people/delete/{userid}')
