def includeme(config):
    # settings = config.registry.settings
    config.add_route('search', 'search/{service_id}/{process_id}/{value}')