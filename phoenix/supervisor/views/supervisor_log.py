from pyramid.view import view_config, view_defaults

from phoenix.views import MyView


@view_defaults(permission='admin', layout='default')
class SupervisorLog(MyView):
    def __init__(self, request):
        super(SupervisorLog, self).__init__(request, name='supervisor_log', title='Log')

    @view_config(route_name='supervisor_log', renderer='../templates/supervisor/supervisor_log.pt')
    def view(self):
        import xmlrpclib
        # TODO: dont use hardcoded urls
        server = xmlrpclib.Server('http://localhost:9001/RPC2')
        name = self.request.matchdict.get('name')

        log = server.supervisor.tailProcessStdoutLog(name, 0, 4096)
        log_list = log[0].split('\n')
        return dict(name=name, log=log_list)
