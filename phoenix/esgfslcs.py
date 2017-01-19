from requests_oauthlib import OAuth2Session

from pyramid.security import authenticated_userid

import logging
LOGGER = logging.getLogger(__name__)


class ESGFSLCSClient(object):
    def __init__(self, request):
        self.request = request
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
