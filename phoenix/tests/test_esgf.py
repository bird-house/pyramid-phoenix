from phoenix.esgf import metadata
from phoenix.esgf import search


def test_convert_constraints():
    converted = metadata.convert_constraints(
        "http://esgf-data.dkrz.de/esg-search/search?project=CMIP5&time_frequency=mon&variable=tas,tasmax,tasmin")  # noqa
    assert converted == 'project:CMIP5,time_frequency:mon,variable:tas,variable:tasmax,variable:tasmin'


def test_build_constraints_dict():
    c_dict = search.build_constraint_dict(
        'project:CMIP5,time_frequency:mon,variable:tas,variable:tasmax,variable:tasmin')
    assert c_dict.getall('variable') == ['tas', 'tasmax', 'tasmin']


def test_date_from_filename():
    date = search.date_from_filename(
        "tas_EUR-44i_ECMWF-ERAINT_evaluation_r1i1p1_HMS-ALADIN52_v1_mon_200101-200812.nc")
    assert date == (2001, 2008)
