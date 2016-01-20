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

import logging
logger = logging.getLogger(__name__)

class ESGF(OpenID):
    """
    ESGF :class:`.OpenID` provider with the :attr:`.provider_url` predefined to ``"https://{hostname}/esgf-idp/openid/{username}"``.
    """

    hostname = 'localhost'
    provider_url = 'https://{hostname}/esgf-idp/openid/{username}'

    def __init__(self, *args, **kwargs):
        super(ESGF, self).__init__(*args, **kwargs)

        # get username
        if 'username' in self.params:
            self.username = self.params.get('username')
            self.identifier = self.provider_url.format(hostname=self.hostname, username=self.username)

class DKRZ(ESGF):
    hostname = 'esgf-data.dkrz.de'

class IPSL(ESGF):
    hostname = 'esgf-node.ipsl.fr'

class BADC(ESGF):
    hostname = 'ceda.ac.uk'
    provider_url = 'https://{hostname}/openid/{username}'

class PCMDI(ESGF):
    hostname = 'pcmdi9.llnl.gov'

class SMHI(ESGF):
    hostname = 'esg-dn1.nsc.liu.se'


PROVIDER_ID_MAP = [DKRZ, IPSL, BADC, PCMDI, SMHI]
        
