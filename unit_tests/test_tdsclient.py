from nose.tools import ok_
from nose import SkipTest
from nose.plugins.attrib import attr

from phoenix.tdsclient import TdsClient

def test_get_objects():
    tds = TdsClient("http://www.esrl.noaa.gov/psd/thredds/catalog.html")
    items = tds.get_objects(tds.catalog_url)
    ok_(len(items['catalogs']) == 2)
    ok_(len(items['datasets']) == 0)
    ok_(items['catalogs'][0].url == "http://www.esrl.noaa.gov/psd/thredds/catalog/Datasets/catalog.xml")
