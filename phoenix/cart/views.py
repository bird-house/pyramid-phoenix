from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound

from phoenix.views import MyView


@view_defaults(permission='submit')
class CartActions(object):
    """Actions related to cart."""

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.session = self.request.session

    @view_config(renderer='json', name='add_to_cart.json')
    def add_to_cart(self):
        url = self.request.params.get('url')
        title = self.request.params.get('title')
        abstract = self.request.params.get('abstract')
        item = self.request.cart.add_item(url, title=title, abstract=abstract)
        if item:
            self.session.flash("Added %s to Cart" % item.filename, queue='info')
        return self.request.cart.to_json()

    @view_config(renderer='json', name='remove_from_cart.json')
    def remove_from_cart(self):
        url = self.request.params.get('url')
        item = self.request.cart.remove_item(url)
        if item:
            self.session.flash("Removed %s from Cart" % item.filename, queue='info')
        return self.request.cart.to_json()

    @view_config(route_name='clear_cart')
    def clear_cart(self):
        self.request.cart.clear()
        self.session.flash("Cart is empty", queue='warning')
        return HTTPFound(self.request.route_path('cart'))

    @view_config(route_name='remove_cart_item')
    def remove_item(self):
        url = self.request.params.get('url')
        if url:
            self.request.cart.remove_item(url)
        return HTTPFound(self.request.route_path('cart'))


@view_defaults(permission='submit', layout='default')
class Cart(MyView):
    def __init__(self, request):
        super(Cart, self).__init__(request, name='cart', title='Cart')

    @view_config(route_name='cart', renderer='templates/cart/cart.pt')
    def view(self):
        return {}
