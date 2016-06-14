import pytest
import unittest

from pyramid import testing

class UserSettingsTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    @pytest.mark.skip(reason="no way of currently testing this")
    def test_user_view(self):
        from phoenix.views import UserSettings

        request = testing.DummyRequest()
        inst = UserSettings(request)
        response = inst.user_view()
        self.assertEqual('Home View', response['name'])

class UserSettingsFunctionalTests(unittest.TestCase):
    def setUp(self):
        pass
        #from phoenix import main
        #app = main({})
        #from webtest import TestApp

        #self.testapp = TestApp(app)

    @pytest.mark.skip(reason="no way of currently testing this")
    def test_user_view(self):
        res = self.testapp.get('/', status=200)
        self.assertIn(b'<h1>Hi Home View', res.body)

