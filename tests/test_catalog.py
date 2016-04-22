from nose.tools import ok_, with_setup
from nose import SkipTest
from nose.plugins.attrib import attr

import __init__ as base


# TODO: need request object to run these tests

def setup():
    raise SkipTest
    models.add_wps(url='http://localhost:8090/wps')

def test_get_wps_list():
    raise SkipTest
    wps_list = models.get_wps_list()
    ok_(len(wps_list) > 0)
