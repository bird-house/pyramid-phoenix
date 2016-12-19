from pyramid.view import view_config

from pyramid.httpexceptions import HTTPFound
from pyramid.security import authenticated_userid

from requests_oauthlib import OAuth2Session

from phoenix.security import generate_access_token
from phoenix.providers.oauth2 import ESGF

import logging
logger = logging.getLogger(__name__)


class Actions(object):
    def __init__(self, request):
        self.request = request
        self.session = request.session
        self.collection = self.request.db.users
        self.userid = self.request.matchdict.get('userid', authenticated_userid(self.request))
        # esgf slcs stuff
        esgf_slcs_url = self.request.registry.settings.get('esgf.slcs.url')
        self.client_id = self.request.registry.settings.get('esgf.slcs.client.id')
        self.client_secret = self.request.registry.settings.get('esgf.slcs.client.secret')
        self.authorize_url = "{}/oauth/authorize".format(esgf_slcs_url)
        self.token_url = "{}/oauth/access_token".format(esgf_slcs_url)
        certificate_url = "{}/oauth/certificate/".format(esgf_slcs_url)
        self.scope = [certificate_url]
        self.redirect_uri = self.request.route_url('oauth_callback')

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

    @view_config(route_name='generate_esgf_slcs_token', permission='submit')
    def generate_esgf_slcs_token(self):
        """
        Redirect the user to the ESGF SLCS Server for authorisation.
        """
        # Reset any existing state in the session
        if 'oauth_state' in self.session:
            del self.session['oauth_state']
        # Generate a new state and the accompanying URL to use for authorisation
        slcs = OAuth2Session(self.client_id, redirect_uri=self.redirect_uri, scope=self.scope)
        auth_url, state = slcs.authorization_url(self.authorize_url)
        # state is used to prevent CSRF - keep for later
        self.session['oauth_state'] = state
        return HTTPFound(location=auth_url)

    @view_config(route_name='oauth_callback', permission='submit')
    def oauth_callback(self):
        """
        Convert an authorisation grant into an access token.
        """
        # If we have not yet entered the OAuth flow, redirect to the start
        if 'oauth_state' not in self.session:
            return HTTPFound(location=self.request.route_path('generate_esgf_slcs_token'))
        # Notify of any errors
        # if 'error' in request.args:
        #     return """
        #     <h1>ESGF SLCS Client Example</h1>
        #
        #     <h2>ERROR: <code>{}</code></h2>
        #
        #     <p><a href="/">Back to menu</a></p>
        #     """.format(request.args.get('error'))
        # Exchange the authorisation grant for a token
        slcs = OAuth2Session(self.client_id,
                             redirect_uri=self.redirect_uri,
                             state=self.session.pop('oauth_state'))
        token = slcs.fetch_token(
            self.token_url,
            client_secret=self.client_secret,
            authorization_response=self.request.url,
            # Don't bother verifying certificates as we are likely using a test SLCS
            # server with a self-signed cert.
            verify=False
        )
        # Store the token in the session
        self.session['esgf_oauth_token'] = token
        # Redirect to the token view
        return HTTPFound(location=self.request.route_path('profile', userid=self.userid, tab='esgf_slcs'))

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
    config.add_route('generate_esgf_slcs_token', 'people/generate_esgf_token')
    config.add_route('oauth_callback', 'oauth_callback')
    config.add_route('delete_user', 'people/delete/{userid}')
