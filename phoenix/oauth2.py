import os
import requests
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient
from phoenix.db import mongodb

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

import logging
LOGGER = logging.getLogger("PHOENIX")


class OAuth2(object):
    def __init__(self, registry):
        self.settings = registry.settings
        self.db = mongodb(registry)
        self.refresh_url = ''
        self.introspect_url = ''
        self.client_id = ''
        self.client_secret = ''
        self.verify = False
        self.scope = 'compute'

    def refresh_token(self, userid):
        user = self.db.users.find_one({'identifier': userid})
        token = user.get('token')
        try:
            client = OAuth2Session(self.client_id, token=token)
            token = client.refresh_token(
                self.refresh_url,
                client_id=self.client_id,
                client_secret=self.client_secret)
        except Exception as e:
            LOGGER.warning("could not refresh token: {}".format(e))
            raise
        else:
            self.db.users.update_one(
                {'identifier': userid},
                {'$set': {'token': token, }})
        return token

    def introspect_access_token(self, access_token):
        resp = requests.post(
            self.introspect_url,
            data={'token': access_token},
            auth=(self.client_id, self.client_secret))
        return resp.json()


class KeycloakClient(OAuth2):
    def __init__(self, registry):
        super(KeycloakClient, self).__init__(registry)
        self.refresh_url = "{}/auth/realms/{}/protocol/openid-connect/token".format(
            self.settings.get('keycloak.url'), self.settings.get('keycloak.realm'))
        self.introspect_url = "{}/auth/realms/{}/protocol/openid-connect/token/introspect".format(
            self.settings.get('keycloak.url'), self.settings.get('keycloak.realm'))
        self.client_id = self.settings.get('keycloak.client.id')
        self.client_secret = self.settings.get('keycloak.client.secret')


class TwitcherClient(OAuth2):
    def __init__(self, registry):
        super(TwitcherClient, self).__init__(registry)
        self.refresh_url = "{}/oauth/token".format(self.settings.get('twitcher.url'))
        self.client_id = self.settings.get('twitcher.client.id')
        self.client_secret = self.settings.get('twitcher.client.secret')

    def refresh_token(self, userid):
        """TODO: implement refresh token in twitcher"""
        return self.fetch_token(userid)

    def introspect_access_token(self, access_token):
        raise NotImplementedError

    def fetch_token(self, userid):
        client = BackendApplicationClient(client_id=self.client_id)
        oauth = OAuth2Session(client=client)
        try:
            token = oauth.fetch_token(
                self.refresh_url,
                scope=self.scope,
                client_id=self.client_id,
                client_secret=self.client_secret,
                include_client_id=True,
                verify=self.verify)
        except Exception as e:
            LOGGER.warning("could not refresh token: {}".format(e))
            raise
        else:
            self.db.users.update_one(
                {'identifier': userid},
                {'$set': {'token': token, }})
        return token


def oauth2_client_factory(registry):
    settings = registry.settings
    if settings.get('keycloak.url'):
        return KeycloakClient(registry)
    else:
        return TwitcherClient(registry)
