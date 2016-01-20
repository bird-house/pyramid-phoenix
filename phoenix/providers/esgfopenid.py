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
import openid
import sys
from openid.fetchers import setDefaultFetcher, HTTPFetcher, HTTPResponse

import logging
logger = logging.getLogger(__name__)

__all__ = ['ESGFOpenID']

USER_AGENT = "python-openid/%s (%s)" % (openid.__version__, sys.platform)
MAX_RESPONSE_KB = 1024
    
def _allowedURL(url):
    return url.startswith('http://') or url.startswith('https://')

class Urllib2Fetcher(HTTPFetcher):
    """An C{L{HTTPFetcher}} that uses urllib2.
    """

    def fetch(self, url, body=None, headers=None):
        if not _allowedURL(url):
            raise ValueError('Bad URL scheme: %r' % (url,))

        if headers is None:
            headers = {}

        headers.setdefault(
            'User-Agent',
            "%s Python-urllib/%s" % (USER_AGENT, urllib2.__version__,))

        req = urllib2.Request(url, data=body, headers=headers)
        try:
            try:
                f = urllib2.urlopen(req, context=ssl._create_unverified_context())
            except:
                logger.exception('urlopen failed')
            try:
                return self._makeResponse(f)
            finally:
                f.close()
        except urllib2.HTTPError, why:
            try:
                return self._makeResponse(why)
            finally:
                why.close()

    def _makeResponse(self, urllib2_response):
        resp = HTTPResponse()
        resp.body = urllib2_response.read(MAX_RESPONSE_KB * 1024)
        resp.final_url = urllib2_response.geturl()
        resp.headers = dict(urllib2_response.info().items())

        if hasattr(urllib2_response, 'code'):
            resp.status = urllib2_response.code
        else:
            resp.status = 200
        return resp

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

        self.identifier = 'https://esgf-data.dkrz.de/esgf-idp/openid/macpingu'

        # use fetcher with disabled ssl verification
        setDefaultFetcher( Urllib2Fetcher() )

PROVIDER_ID_MAP = [ESGFOpenID]
        
