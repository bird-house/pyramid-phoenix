"""
|oauth2| Providers
-------------------

Providers which implement the |oauth2|_ protocol.

    ESGF SLCS Server
"""

from authomatic.providers.oauth2 import OAuth2

__all__ = ['ESGF']


class ESGF(OAuth2):
    """
    See example: https://github.com/cehbrecht/esgf-slcs-client-example
    """
    esgf_slcs_url = "https://172.28.128.4"
    user_authorization_url = "{}/oauth/authorize".format(esgf_slcs_url)
    access_token_url = "{}/oauth/access_token".format(esgf_slcs_url)
    certificate_url = "{}/oauth/certificate/".format(esgf_slcs_url)
    user_info_url = ''
    user_info_scope = [certificate_url]

    @staticmethod
    def _x_user_parser(user, data):
        user.id = user.username = data.get('user')
        return user

PROVIDER_ID_MAP = [ESGF]
