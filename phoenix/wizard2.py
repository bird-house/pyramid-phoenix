from pyramid.view import view_config, view_defaults

@view_defaults(permission='edit', layout='default')
class Wizard:
    def __init__(self, request):
        self.request = request
        self.session = self.request.session

    @view_config(route_name='csw', renderer='templates/csw.pt')
    def csw_view(self):
        if 'next' in self.request.POST:
            return HTTPFound(location=self.request.route_url('csw'))
        elif 'previous' in self.request.POST:
            return HTTPFound(location=self.request.route_url('csw'))
        elif 'cancel' in self.request.POST:
            return HTTPFound(location=self.request.route_url('csw'))    

        return dict(title="Catalog Viewer", description="Search in Catalog Service")
