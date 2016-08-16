import pytest
import unittest
from pyramid import testing

from phoenix.cart import Cart


def test_cart():
    request = testing.DummyRequest()
    cart = Cart(request)
    assert cart.has_items() is False

    url = "http://localhost/download/test.nc"
    cart.add_item(url=url)
    assert cart.has_items()
    assert cart.num_items() == 1

    for item in cart:
        assert item.download_url() == url

    cart.remove_item(url)
    assert cart.has_items() is False


class CartTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    @pytest.mark.skip(reason="no way of currently testing this")
    def test_cart_from_request(self):
        request = testing.DummyRequest()
        request.cart is not None




