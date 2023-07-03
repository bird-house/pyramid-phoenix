def includeme(config):
    # needs settings
    # config.include('phoenix.settings')

    # settings = config.registry.settings
    config.add_route('people', 'people')
    config.add_route('profile', 'people/profile/{userid}/{tab}')
    # actions
    config.include('phoenix.people.views.actions')
