from nose.tools import ok_, with_setup
from nose import SkipTest
from nose.plugins.attrib import attr

from phoenix import wizard

SERVICE = "http://localhost:8090/wps"

def test_convert_states_to_nodes():
    states = [{}, {}, {}, {'file_identifier': ['test1.nc']}, {}, {}]
    
    nodes = wizard.convert_states_to_nodes(SERVICE, states)
    ok_('test1.nc' in str(nodes), nodes)
