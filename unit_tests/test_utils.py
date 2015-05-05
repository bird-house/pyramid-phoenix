from nose.tools import ok_, with_setup
from nose import SkipTest
from nose.plugins.attrib import attr

from phoenix import utils

def test_quote_wps_params():
    raise SkipTest
    result = helpers.quote_wps_params( [('url', u'http://localhost:8090/test')])
    ok_(result[0][1] == 'http%3A//localhost%3A8090/test', result)

def test_unquote_wps_params():
    raise SkipTest
    result = helpers.unquote_wps_params( [('url', 'http%3A//localhost%3A8090/test')])
    ok_(result[0][1] == 'http://localhost:8090/test', result)

def test_filesizeformat():
    ok_(utils.filesizeformat(None) == '0 Bytes')
    ok_(utils.filesizeformat(100)  == '100.00 Bytes')
    ok_(utils.filesizeformat('1001') == '1001.00 Bytes')
    ok_(utils.filesizeformat('abc2000001') == '0 Bytes')
    ok_(utils.filesizeformat('nix') == '0 Bytes')
    ok_(utils.filesizeformat('20 30') == '0 Bytes')
    ok_(utils.filesizeformat(300000000) == '286.10 MB')
    ok_(utils.filesizeformat('500000000000') == '465.66 GB')
    ok_(utils.filesizeformat('40000000000000') == '36.38 TB')
    


