from .cart import Cart, CartItem


def includeme(config):
    def get_cart(request):
        return Cart(request)
    config.add_request_method(get_cart, 'cart', reify=True)

    config.add_route('cart', 'cart')
    config.add_route('clear_cart', 'cart/clear')
    config.add_route('remove_cart_item', 'cart/remove')


