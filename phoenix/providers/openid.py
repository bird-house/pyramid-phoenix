"""
|openid| Providers
----------------------------------
Providers which implement the |openid|_ protocol based on the
`python-openid`_ library.
.. warning::
    This providers are dependent on the |pyopenid|_ package.
"""

from authomatic.providers.openid import OpenID

#from openid.fetchers import setDefaultFetcher, Urllib2Fetcher
#setDefaultFetcher(Urllib2Fetcher())


class DKRZ(OpenID):
    """
    DKRZ :class:`.OpenID` provider with the :attr:`.identifier` predefined to ``"https://esgf-data.dkrz.de/esgf-idp/openid/id"``.
    """
    
    identifier = 'https://esgf-data.dkrz.de/esgf-idp/openid/id'
