from nose.tools import ok_, with_setup
from nose import SkipTest
from nose.plugins.attrib import attr

import __init__ as base

from phoenix import wizard

def test_convert_states_to_nodes():
    raise SkipTest
    states = [{}, {}, {}, {'file_identifier': ['test1.nc']}, {}, {}]
    
    nodes = wizard.convert_states_to_nodes(base.SERVICE, states)
    ok_('test1.nc' in str(nodes), nodes)
