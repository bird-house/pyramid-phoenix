def includeme(config):
    config.add_route('processes', '/processes')
    config.add_route('processes_list', '/processes/list')
    config.add_route('processes_execute', '/processes/execute')
