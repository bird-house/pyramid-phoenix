from nose.tools import ok_, with_setup
from nose import SkipTest
from nose.plugins.attrib import attr

from phoenix import helpers

from owslib.wps import WebProcessingService, monitorExecution

SERVICE = "http://localhost:8090/wps"
WPS = WebProcessingService(SERVICE, verbose=True)
NODES = None

def setup_nodes():
    global NODES
    
    source = dict(
        service = SERVICE,
        identifier = "org.malleefowl.storage.testfiles.source",
        input = [],
        output = ['output'],
        sources = [['test1.nc'], ['test2.nc']]
        )
    worker = dict(
        service = SERVICE,
        identifier = "de.dkrz.cdo.sinfo.worker",
        input = [],
        output = ['output'])
    NODES = dict(source=source, worker=worker)

def test_quote_wps_params():
    result = helpers.quote_wps_params( [('url', u'http://localhost:8090/test')])
    ok_(result[0][1] == 'http%3A//localhost%3A8090/test', result)

def test_unquote_wps_params():
    result = helpers.unquote_wps_params( [('url', 'http%3A//localhost%3A8090/test')])
    ok_(result[0][1] == 'http://localhost:8090/test', result)

@attr('online')
@with_setup(setup_nodes)
def test_execute_restflow():
    execution = helpers.execute_restflow(WPS, NODES)
    monitorExecution(execution, sleepSecs=1)
    result = execution.processOutputs[0].reference
    ok_('wpsoutputs' in result, result)
