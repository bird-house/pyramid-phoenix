import pytest
import unittest
from pyramid import testing
from phoenix.esgf import search
from phoenix.esgf.search import ESGFSearch


def test_build_constraints_dict():
    c_dict = search.build_constraint_dict(
        'project:CMIP5,time_frequency:mon,variable:tas,variable:tasmax,variable:tasmin')
    assert c_dict.getall('variable') == ['tas', 'tasmax', 'tasmin']


def test_date_from_filename():
    date = search.date_from_filename(
        "tas_EUR-44i_ECMWF-ERAINT_evaluation_r1i1p1_HMS-ALADIN52_v1_mon_200101-200812.nc")
    assert date == (2001, 2008)


def test_temporal_filter():
    assert search.temporal_filter(
        "tas_EUR-44i_ECMWF-ERAINT_evaluation_r1i1p1_HMS-ALADIN52_v1_mon_200101-200812.nc") is True
    assert search.temporal_filter(
        "tas_EUR-44i_ECMWF-ERAINT_evaluation_r1i1p1_HMS-ALADIN52_v1_mon_200101-200812.nc",
        2001, 2008) is True
    assert search.temporal_filter(
        "tas_EUR-44i_ECMWF-ERAINT_evaluation_r1i1p1_HMS-ALADIN52_v1_mon_200101-200812.nc",
        2009, 2010) is False
    assert search.temporal_filter(
        "tas_EUR-44i_ECMWF-ERAINT_evaluation_r1i1p1_HMS-ALADIN52_v1_mon_200101-200812.nc",
        1990, 2000) is False


def test_variable_filter():
    c_dict = search.build_constraint_dict(
        'variable:tas,variable:tasmax,variable:tasmin')
    assert search.variable_filter(c_dict, {'variable': ['tas']}) is True
    assert search.variable_filter(c_dict, {'variable': ['pr']}) is False


class ESGFSearchTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_query_params(self):
        request = testing.DummyRequest()
        esgfsearch = ESGFSearch(request, url='https://esgf-data.dkrz.de/esg-search')
        params = esgfsearch.query_params()
        assert params['distrib'] == 'false'
        assert params['start'] == 2001
        assert params['end'] == 2005

    def test_params(self):
        request = testing.DummyRequest()
        esgfsearch = ESGFSearch(request, url='https://esgf-data.dkrz.de/esg-search')
        params = esgfsearch.params()
        assert params['distrib'] is False
        assert params['start'].year == 2001
        assert params['end'].year == 2005

    @pytest.mark.online
    def test_search_datasets(self):
        request = testing.DummyRequest()
        esgfsearch = ESGFSearch(request, url='https://esgf-data.dkrz.de/esg-search')
        result = esgfsearch.search_datasets()
        assert len(result['projects'])
        assert len(result['categories'])
