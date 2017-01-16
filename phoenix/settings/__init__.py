import logging
logger = logging.getLogger(__name__)


def load_settings(request):
    defaults = dict(solr_maxrecords=-1, solr_depth=2)

    collection = request.db.settings
    settings = collection.find_one()
    if not settings:
        collection.save(defaults)
        settings = collection.find_one()
    for key in defaults.keys():
        if not key in settings:
            settings[key] = defaults[key]
    return settings


def includeme(config):
    settings = config.registry.settings

    logger.info('Add Settings')

    config.add_route('settings', '/settings')
    config.add_route('settings_auth', '/settings/auth')
    config.add_route('settings_ldap', '/settings/ldap')
    config.add_route('settings_github', '/settings/github')
    config.add_route('settings_esgf', '/settings/esgf')
    config.add_route('settings_solr', '/settings/solr/{tab}')

    def github_oauth(request):
        db = request.registry.settings['db']
        entry = db.settings.find_one()
        entry = entry or {}
        return entry.get('github', {})
    config.add_request_method(github_oauth, reify=True)

    def esgf_oauth(request):
        db = request.registry.settings['db']
        entry = db.settings.find_one()
        entry = entry or {}
        return entry.get('esgf_slcs', {})
    config.add_request_method(esgf_oauth, reify=True)
