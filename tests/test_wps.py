import pytest

import __init__ as base

#from phoenix import wps
from owslib.wps import monitorExecution

NODES = None

def setup_nodes():
    global NODES
    
    source = dict(
        service = base.SERVICE,
        identifier = "org.malleefowl.storage.testfiles.source",
        input = [],
        output = ['output'],
        sources = [['test1.nc'], ['test2.nc']]
        )
    worker = dict(
        service = base.SERVICE,
        identifier = "de.dkrz.cdo.sinfo.worker",
        input = [],
        output = ['output'])
    NODES = dict(source=source, worker=worker)

@pytest.mark.online
def test_get_wps():
    my_wps = wps.get_wps(base.SERVICE)
    assert my_wps != None

@pytest.mark.skip(reason="no way of currently testing this")
def test_build_request_url():
    url = wps.build_request_url(
        base.SERVICE,
        identifier="org.malleefowl.test.whoareyou",
        inputs = [('username', 'pingu')],
        output = 'output')
    assert 'pingu' in url

@pytest.mark.online
def test_execute_with_url():
    url = wps.build_request_url(
        base.SERVICE,
        identifier="org.malleefowl.test.whoareyou",
        inputs = [('username', 'pingu')],
        output = 'output')
    assert 'pingu' in url

    result = wps.execute_with_url(url)
    assert 'Hello pingu' in result

@pytest.mark.online
def test_execute():
    result = wps.execute(
        base.SERVICE,
        identifier="org.malleefowl.test.whoareyou",
        inputs = [('username', 'pingu')],
        output = 'output')
    assert 'Hello pingu' in result

@pytest.mark.online
def test_get_token():
    my_wps = wps.get_wps(base.SERVICE)
    token = wps.get_token(my_wps, userid="alex@nowhere.org")
    assert 'alex' in token
    
@pytest.mark.online
@pytest.mark.skip(reason="needs nose.with_setup")
def test_execute_restflow():
    global NODES

    my_wps = wps.get_wps(base.SERVICE)
    
    execution = wps.execute_restflow(my_wps, NODES)
    monitorExecution(execution, sleepSecs=1)
    result = execution.processOutputs[0].reference
    assert 'wpsoutputs' in result

