from OpenSSL import crypto
from base64 import b64encode
from StringIO import StringIO

from requests_oauthlib import OAuth2Session

from pyramid.security import authenticated_userid

import logging
LOGGER = logging.getLogger(__name__)


class ESGFSLCSClient(object):
    def __init__(self, request):
        self.request = request
        self.session = self.request.session
        settings = self.request.registry.settings
        self.collection = self.request.db.users
        self.userid = authenticated_userid(self.request)
        # slcs stuff
        esgf_slcs_url = settings.get('esgf.slcs.url')
        self.client_id = settings.get('esgf.slcs.client.id')
        self.client_secret = settings.get('esgf.slcs.client.secret')
        self.authorize_url = "{}/oauth/authorize".format(esgf_slcs_url)
        self.token_url = "{}/oauth/access_token".format(esgf_slcs_url)
        self.refresh_url = self.token_url
        self.certificate_url = "{}/oauth/certificate/".format(esgf_slcs_url)
        self.scope = [self.certificate_url]
        self.redirect_uri = self.request.route_url('esgf_oauth_callback')

    def authorize(self):
        """
        Redirect the user to the ESGF SLCS Server for authorisation.
        """
        # Reset any existing state in the session
        if 'oauth_state' in self.session:
            del self.session['oauth_state']
        # Generate a new state and the accompanying URL to use for authorisation
        client = OAuth2Session(self.client_id, redirect_uri=self.redirect_uri, scope=self.scope)
        auth_url, state = client.authorization_url(self.authorize_url)
        # state is used to prevent CSRF - keep for later
        self.session['oauth_state'] = state
        return auth_url

    def callback(self):
        """
        Convert an authorisation grant into an access token.
        """
        # If we have not yet entered the OAuth flow, redirect to the start
        if 'oauth_state' not in self.session:
            return False
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
        # Store the token in the database
        self.save_token(token)
        return True

    def refresh_token(self):
        token = self.get_token()
        if not token:
            return False
        else:
            token['expires_in'] = '-30'  # need to be negative to refresh token

        extra = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        }

        client = OAuth2Session(self.client_id, token=token)
        token = client.refresh_token(self.refresh_url, verify=False, **extra)
        self.save_token(token)
        LOGGER.debug('refresh token done.')
        return True

    def get_token(self):
        user = self.collection.find_one({'identifier': self.userid})
        token = user.get('esgf_token')
        return token

    def save_token(self, token):
        """
        Store the token in the database.
        """
        if self.userid:
            self.collection.update_one(
                {'identifier': self.userid},
                {'$set': {'esgf_token': token, }})

    def get_certificate(self):
        """
        Generates a new private key and certificate request, submits the request to be
        signed by the SLCS CA and prints the resulting key/certificate pair.

        Uses automatic refreshing of tokens if they have expired.
        """
        token = self.get_token()
        if not token:
            return False
        # Generate a new key pair
        key_pair = crypto.PKey()
        key_pair.generate_key(crypto.TYPE_RSA, 2048)
        private_key = crypto.dump_privatekey(crypto.FILETYPE_PEM, key_pair).decode("utf-8")
        # Generates a certificate request using the key pair
        cert_request = crypto.X509Req()
        cert_request.set_pubkey(key_pair)
        cert_request.sign(key_pair, "md5")
        cert_request = crypto.dump_certificate_request(crypto.FILETYPE_ASN1, cert_request)
        # Build th oauth session object
        client = OAuth2Session(
            self.client_id,
            token=token,
            auto_refresh_url=self.refresh_url,
            auto_refresh_kwargs={
                'client_id': self.client_id,
                'client_secret': self.client_secret,
            },
            # Update the token with the new token if it is refreshed
            token_updater=self.save_token,
        )
        response = client.post(
            self.certificate_url,
            data={'certificate_request': b64encode(cert_request)},
            verify=False
        )
        # Store credentials
        stored_credentials = self.request.storage.save_file(
            StringIO(response.text),
            filename="credentials.pem",
            folder="esgf_certs",
            extensions=('pem',),
            randomize=True)
        user = self.collection.find_one({'identifier': self.userid})
        user['credentials'] = self.request.storage.url(stored_credentials)
        self.collection.update({'identifier': self.userid}, user)
        return True
