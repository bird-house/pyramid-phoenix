import pytest

import __init__ as base

from phoenix import wizard


@pytest.mark.skip(reason="no way of currently testing this")
def test_convert_states_to_nodes():
    states = [{}, {}, {}, {'file_identifier': ['test1.nc']}, {}, {}]
    
    nodes = wizard.convert_states_to_nodes(base.SERVICE, states)
    assert 'test1.nc' in str(nodes)
