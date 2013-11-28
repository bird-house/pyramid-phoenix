import nose.tools
from nose import SkipTest

from phoenix import helpers

def test_quote_wps_params():
    result = helpers.quote_wps_params( [('url', u'http://localhost:8090/test')])
    nose.tools.ok_(result[0][1] == 'http%3A//localhost%3A8090/test', result)

def test_unquote_wps_params():
    result = helpers.unquote_wps_params( [('url', 'http%3A//localhost%3A8090/test')])
    nose.tools.ok_(result[0][1] == 'http://localhost:8090/test', result)
