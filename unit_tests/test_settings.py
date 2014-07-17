import unittest

from pyramid import testing

class UserSettingsTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_user_view(self):
        from phoenix.views import UserSettings

        request = testing.DummyRequest()
        inst = UserSettings(request)
        response = inst.user_view()
        self.assertEqual('Home View', response['name'])

