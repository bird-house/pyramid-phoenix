from datetime import datetime, timedelta

from phoenix import utils

def test_time_ago_in_words():
    assert utils.time_ago_in_words(datetime.now() - timedelta(minutes=1)) == '1 minute ago'
    assert utils.time_ago_in_words(datetime.now() - timedelta(hours=1, minutes=7)) == '1 hour ago'
    assert utils.time_ago_in_words(datetime.now() - timedelta(hours=1, minutes=1)) == '1 hour ago'
    assert utils.time_ago_in_words(datetime.now() - timedelta(days=1, hours=1)) == '1 day ago'
    assert utils.time_ago_in_words(datetime.now() - timedelta(days=31, hours=1)) == '1 month ago'
    assert utils.time_ago_in_words(datetime.now() - timedelta(days=366, hours=1)) == '1 year ago'
    assert utils.time_ago_in_words('nothing') == '???'
    
def test_make_tags():
    assert utils.make_tags("main,dev") == ['dev', 'main']
    assert utils.make_tags("main,dev,Testing") == ['dev', 'main', 'testing']
    assert utils.make_tags("public, dev,Testing , Next Generation, ,,; ") == [';', 'dev', 'next generation', 'public', 'testing']
    

