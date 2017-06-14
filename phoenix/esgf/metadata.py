from owslib.wps import WebProcessingService

from phoenix._compat import urlparse

import logging
LOGGER = logging.getLogger("PHOENIX")

ROLE_CONSTRAINTS = 'https://www.earthsystemcog.org/spec/esgf_search/2.1.0/def/constraints'


def process_constraints(url, identifier):
    wps = WebProcessingService(url, verify=False, skip_caps=True)
    process = wps.describeprocess(identifier)
    for metadata in process.metadata:
        if metadata.role == ROLE_CONSTRAINTS and metadata.url:
            LOGGER.debug("constraints=%s", metadata.url)
            parsed_url = urlparse(metadata.url)
            return parsed_url.query
    return None
