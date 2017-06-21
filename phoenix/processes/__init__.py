def includeme(config):
    settings = config.registry.settings

    config.add_route('processes', '/processes')
    config.add_route('processes_list', '/processes/list')
    config.add_route('processes_execute', '/processes/execute')

    config.include('phoenix.processes.views.actions')
