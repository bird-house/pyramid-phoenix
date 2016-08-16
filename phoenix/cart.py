def includeme(config):

    def cart(request):
        return Cart()
    config.add_request_method(cart, reify=True)


class CartItem(object):
    def __init__(self, url):
        self.url = url

    def download_url(self):
        return self.url


class Cart(object):

    def __init__(self, request):
        self.request = request
        self.session = request.session
        # load items
        self.items = self.session.get('cart', {})

    def __iter__(self):
        """
        Allow the cart to be iterated giving access to the cart's items.
        """
        for key in self.items:
            yield self.items[key]

    def add_item(self, url):
        item = CartItem(url)
        self.items[url] = item
        self.save()

    def remove_item(self, url):
        if url in self.items:
            del self.items[url]
        self.save()

    def num_items(self):
        return len(self.items)

    def has_items(self):
        return self.num_items() > 0

    def save(self):
        self.session['cart'] = self.items
        self.session.changed()
