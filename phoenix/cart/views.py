from pyramid.view import view_config, view_defaults

from phoenix.views import MyView


@view_defaults(permission='edit', layout='default')
class Cart(MyView):
    def __init__(self, request):
        super(Cart, self).__init__(request, name='cart', title='Cart')

    @view_config(route_name='cart', renderer='phoenix:cart/templates/cart/cart.pt')
    def view(self):
        return {}
