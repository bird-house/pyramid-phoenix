"""
|oauth2| Providers
-------------------

Providers which implement the |oauth2|_ protocol.

    Ceda
"""

from authomatic.providers.oauth2 import OAuth2

__all__ = ['Ceda']


class Ceda(OAuth2):
    """
    TODO: ask Phil :)
    """
    user_authorization_url = 'https://slcs.ceda.ac.uk/oauth/authorize'
    access_token_url = 'https://slcs.ceda.ac.uk/oauth/access_token'
    user_info_url = ''

    user_info_scope = ['https://slcs.ceda.ac.uk/oauth/certificate/']

    @staticmethod
    def _x_user_parser(user, data):
        user.id = user.username = data.get('user')
        return user

PROVIDER_ID_MAP = [Ceda]
