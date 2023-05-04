from pyramid.view import view_config

@view_config(route_name='search', renderer='json', request_method="POST", xhr=False, accept="application/json")
def search(request):
    result = {"success": False}
    return result