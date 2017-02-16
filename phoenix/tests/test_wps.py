from lxml import etree
from .common import WPS_RESPONSE_XML

from phoenix import wps


def test_check_status():
    doc = etree.parse(WPS_RESPONSE_XML)
    execution = wps.check_status(response=etree.tostring(doc), sleep_secs=0)
    assert execution.response is not None
    assert isinstance(execution.response, etree._Element)
    assert execution.isSucceded()
    assert execution.statusLocation ==\
        'https://localhost:28090/wpsoutputs/hummingbird/56cd4294-bd69-11e6-80fe-68f72837e1b4.xml'
