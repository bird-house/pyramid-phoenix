from pyramid.view import view_config

from pyramid.httpexceptions import HTTPFound
from pyramid.security import authenticated_userid

from phoenix.security import generate_access_token

import logging
logger = logging.getLogger(__name__)


class Actions(object):
    def __init__(self, request):
        self.request = request
        self.session = request.session
        self.collection = self.request.db.users
        self.userid = self.request.matchdict.get('userid', authenticated_userid(self.request))

    @view_config(route_name='forget_esgf_certs', permission='submit')
    def forget_esgf_certs(self):
        user = self.collection.find_one({'identifier': self.userid})
        user['credentials'] = None
        user['cert_expires'] = None
        self.collection.update({'identifier': self.userid}, user)
        self.session.flash("ESGF Certficate removed.", queue='info')
        return HTTPFound(location=self.request.route_path('profile', userid=self.userid, tab='esgf'))

    @view_config(route_name='generate_twitcher_token', permission='submit')
    def generate_twitcher_token(self):
        generate_access_token(self.request.registry, self.userid)
        return HTTPFound(location=self.request.route_path('profile', userid=self.userid, tab='twitcher'))

    @view_config(route_name='delete_user', permission='admin')
    def delete_user(self):
        if self.userid:
            self.collection.remove(dict(identifier=self.userid))
            self.session.flash('User removed', queue="info")
        return HTTPFound(location=self.request.route_path('people'))


def includeme(config):
    """ Pyramid includeme hook.
    :param config: app config
    :type config: :class:`pyramid.config.Configurator`
    """
    config.add_route('forget_esgf_certs', 'people/forget_esgf_certs')
    config.add_route('generate_twitcher_token', 'people/gentoken')
    config.add_route('delete_user', 'people/delete/{userid}')
