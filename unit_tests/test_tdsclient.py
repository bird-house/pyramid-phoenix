from nose.tools import ok_
from nose import SkipTest
from nose.plugins.attrib import attr

from phoenix import tdsclient

def test_get_objects():
    tds = tdsclient.TdsClient("http://www.esrl.noaa.gov/psd/thredds/catalog.html")
    items = tds.get_objects(tds.catalog_url)
    ok_(len(items) > 0)
    ok_(items[0].url() == "http://www.esrl.noaa.gov/psd/thredds/catalog/Datasets/catalog.xml")

def test_get_objects_2():
    tds = tdsclient.TdsClient("http://www.esrl.noaa.gov/psd/thredds/catalog/Datasets/ncep.reanalysis2.dailyavgs/surface/catalog.xml")
    items = tds.get_objects(tds.catalog_url)
    ok_(len(items) > 0)
    ok_(items[0].url() == "http://www.esrl.noaa.gov/psd/thredds/fileServer/Datasets/ncep.reanalysis2.dailyavgs/surface/hgt.sfc.nc")
    ok_(items[0].bytes() == 24030)
    ok_(items[0].modified() == "2010-08-19T21:22:40Z")

def test_dataset_services():
    services = tdsclient.dataset_services(dataset_url='http://www.esrl.noaa.gov/psd/thredds/catalog/Datasets/ncep.reanalysis2.dailyavgs/surface/catalog.xml?dataset=Datasets/ncep.reanalysis2.dailyavgs/surface/mslp.1979.nc')
    ok_(len(services) > 0)
