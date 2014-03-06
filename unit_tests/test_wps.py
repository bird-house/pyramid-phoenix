from nose.tools import ok_, with_setup
from nose import SkipTest
from nose.plugins.attrib import attr

import __init__ as base

from phoenix import wps
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

@attr('online')
def test_get_wps():
    my_wps = wps.get_wps(base.SERVICE)
    ok_(my_wps != None, base.SERVICE)

def test_build_request_url():
    url = wps.build_request_url(
        base.SERVICE,
        identifier="org.malleefowl.test.whoareyou",
        inputs = [('username', 'pingu')],
        output = 'output')
    ok_('pingu' in url, url)

@attr('online')
def test_execute_with_url():
    url = wps.build_request_url(
        base.SERVICE,
        identifier="org.malleefowl.test.whoareyou",
        inputs = [('username', 'pingu')],
        output = 'output')
    ok_('pingu' in url, url)

    result = wps.execute_with_url(url)
    ok_('Hello pingu' in result, result)

@attr('online')
def test_execute():
    result = wps.execute(
        base.SERVICE,
        identifier="org.malleefowl.test.whoareyou",
        inputs = [('username', 'pingu')],
        output = 'output')
    ok_('Hello pingu' in result, result)

@attr('online')
def test_get_token():
    my_wps = wps.get_wps(base.SERVICE)
    token = wps.get_token(my_wps, userid="alex@nowhere.org")
    ok_('alex' in token, token)
    
@attr('online')
@with_setup(setup_nodes)
def test_execute_restflow():
    global NODES

    my_wps = wps.get_wps(base.SERVICE)
    
    execution = wps.execute_restflow(my_wps, NODES)
    monitorExecution(execution, sleepSecs=1)
    result = execution.processOutputs[0].reference
    ok_('wpsoutputs' in result, result)

