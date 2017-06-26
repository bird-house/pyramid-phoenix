import unittest

from phoenix.geoform.form import BBoxValidator
from phoenix.geoform.form import URLValidator


def invalid_exc(func, *arg, **kw):
    from colander import Invalid
    try:
        func(*arg, **kw)
    except Invalid as e:
        return e
    else:
        raise AssertionError('Invalid not raised')  # pragma: no cover


class TestBBoxValidator(unittest.TestCase):
    def test_default(self):
        validator = BBoxValidator()
        self.assertEqual(validator(None, "-180,-90,180,90"), None)

    def test_minx(self):
        validator = BBoxValidator()
        e = invalid_exc(validator, None, "-181,-90,180,90")
        self.assertEqual(e.msg, 'MinX out of range [-180, 180].')

    def test_miny(self):
        validator = BBoxValidator()
        e = invalid_exc(validator, None, "0,-91,180,90")
        self.assertEqual(e.msg, 'MinY out of range [-90, 90].')

    def test_maxx(self):
        validator = BBoxValidator()
        e = invalid_exc(validator, None, "0,-90,181,90")
        self.assertEqual(e.msg, 'MaxX out of range [-180, 180].')

    def test_maxy(self):
        validator = BBoxValidator()
        e = invalid_exc(validator, None, "0,-90,180,91")
        self.assertEqual(e.msg, 'MaxY out of range [-90, 90].')


class TestURLValidator(unittest.TestCase):
    def test_default(self):
        validator = URLValidator()
        self.assertEqual(validator(None, "http://somewhere/test.txt"), None)
        self.assertEqual(validator(None, "https://somewhere/test.txt"), None)

    def test_file_scheme(self):
        validator = URLValidator()
        e = invalid_exc(validator, None, "file:///var/lib/test.txt")
        self.assertEqual(e.msg, 'URL scheme file is not allowed.')

    def test_invalid_url(self):
        validator = URLValidator()
        e = invalid_exc(validator, None, "http://")
        self.assertEqual(e.msg, 'Invalid URL.')
