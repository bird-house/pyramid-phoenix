from owslib.wps import WebProcessingService
from pyesgf.multidict import MultiDict

from phoenix._compat import urlparse

import logging
LOGGER = logging.getLogger("PHOENIX")

ROLE_CONSTRAINTS = 'https://www.earthsystemcog.org/spec/esgf_search/4.12.0/def/constraints'


def process_constraints(url, identifier):
    wps = WebProcessingService(url, verify=False, skip_caps=True)
    process = wps.describeprocess(identifier)
    for metadata in process.metadata:
        if metadata.role == ROLE_CONSTRAINTS and metadata.url:
            LOGGER.debug("constraints=%s", metadata.url)
            return convert_constraints(metadata.url)
    return None


def convert_constraints(url):
    """
    converts esgf search query to constraints parameter.
    TODO: constraints parameter should have the same structure as the esgf query.
    """
    # FROM: project=CMIP5&time_frequency=mon&variable=tas,tasmax,tasmin
    # TO: project:CORDEX,experiment:historical,experiment:rcp26
    parsed_url = urlparse(url)
    constraints = MultiDict()
    for qpart in parsed_url.query.split('&'):
        key, value = qpart.split('=')
        for val in value.split(','):
            constraints.add(key.strip(), val.strip())
    converted = ','.join(["{0[0]}:{0[1]}".format(c) for c in constraints.iteritems()])
    return converted
