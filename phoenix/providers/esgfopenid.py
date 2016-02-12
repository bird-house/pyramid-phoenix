"""
|openid| Providers
----------------------------------
Providers which implement the |openid|_ protocol based on the
`python-openid`_ library.
.. warning::
    This providers are dependent on the |pyopenid|_ package.
"""

import urllib2
import ssl
from authomatic.providers.openid import OpenID
from openid.fetchers import setDefaultFetcher, Urllib2Fetcher

import logging
logger = logging.getLogger(__name__)

__all__ = ['ESGFOpenID']

class MyFetcher(Urllib2Fetcher):
    @staticmethod
    def _urlopen(req):
        return urllib2.urlopen(req, context=ssl._create_unverified_context()) 
    urlopen = _urlopen


class ESGFOpenID(OpenID):
    """
    ESGF :class:`.OpenID` provider with a common provider url template ``"https://{hostname}/esgf-idp/openid/{username}"``.
    """

    def __init__(self, *args, **kwargs):
        """
        Accepts additional keyword arguments:
        
        :param hostname:
            The hostname of the ESGF OpenID provider. Default: localhost

        :param provider_url:
            The provider identifier url template. Default: https://{hostname}/esgf-idp/openid/{username}
        """
        super(ESGFOpenID, self).__init__(*args, **kwargs)

        self.hostname = self._kwarg(kwargs, 'hostname', 'localhost')
        self.provider_url = self._kwarg(kwargs, 'provider_url', 'https://{hostname}/esgf-idp/openid/{username}')

        # if username is given set provider identifier using the provider url
        if 'username' in self.params:
            self.username = self.params.get('username')
            self.identifier = self.provider_url.format(hostname=self.hostname, username=self.username)

        # use fetcher with disabled ssl verification
        setDefaultFetcher( MyFetcher() )

PROVIDER_ID_MAP = [ESGFOpenID]
        
