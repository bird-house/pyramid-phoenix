from nose.tools import ok_, with_setup
from nose import SkipTest
from nose.plugins.attrib import attr

from datetime import datetime, timedelta

from phoenix import utils

def test_time_ago_in_words():
    ok_(utils.time_ago_in_words(datetime.now() + timedelta(minutes=1)) == '1 minute ago' )
    ok_(utils.time_ago_in_words(datetime.now() + timedelta(hours=1, minutes=7)) == '1 hour ago' )
    ok_(utils.time_ago_in_words(datetime.now() + timedelta(hours=1, minutes=1)) == '1 hour ago' )
    ok_(utils.time_ago_in_words(datetime.now() + timedelta(days=1, hours=1)) == '1 day ago' )
    ok_(utils.time_ago_in_words(datetime.now() + timedelta(days=31, hours=1)) == '1 month ago' )
    ok_(utils.time_ago_in_words(datetime.now() + timedelta(days=366, hours=1)) == '1 year ago')
    ok_(utils.time_ago_in_words('nothing') == '???')
    

