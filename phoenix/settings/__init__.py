import logging
logger = logging.getLogger(__name__)

def includeme(config):
    settings = config.registry.settings

    logger.info('Add Settings')

    config.add_route('settings', '/settings')
    config.add_route('settings_users', '/settings/users')
    config.add_route('settings_edit_user', '/settings/users/{userid}/edit')
    config.add_route('remove_user', '/settings/users/{userid}/remove')
    config.add_route('settings_monitor', '/settings/monitor')
    config.add_route('settings_auth', '/settings/auth')
    config.add_route('settings_ldap', '/settings/ldap')
    config.add_route('settings_github', '/settings/github')
    config.add_route('settings_solr', '/settings/solr/{tab}')
