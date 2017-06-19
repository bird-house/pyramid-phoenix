from phoenix.esgf import metadata


def test_convert_constraints():
    converted = metadata.convert_constraints(
        "http://esgf-data.dkrz.de/esg-search/search?project=CMIP5&time_frequency=mon&variable=tas,tasmax,tasmin")  # noqa
    assert converted == 'project:CMIP5,time_frequency:mon,variable:tas,variable:tasmax,variable:tasmin'
