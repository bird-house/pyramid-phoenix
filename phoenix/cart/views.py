from pyramid.view import view_config, view_defaults

from phoenix.views import MyView


@view_config(renderer='json', name='add_to_cart.json')
def add_to_cart(request):
    url = request.params.get('url')
    request.cart.add_item(url)
    return request.cart.to_json()


@view_defaults(permission='submit', layout='default')
class Cart(MyView):
    def __init__(self, request):
        super(Cart, self).__init__(request, name='cart', title='Cart')

    @view_config(route_name='cart', renderer='templates/cart/cart.pt')
    def view(self):
        return {}
