import __init__ as base

from phoenix.catalog import doc2record

def test_doc2record():
    record = doc2record({'_id': '123', 'title': 'test doc'})
    assert record.title == 'test doc'
