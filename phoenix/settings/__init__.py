import logging
logger = logging.getLogger(__name__)


def load_settings(request):
    defaults = dict(solr_maxrecords=-1, solr_depth=2)

    settings = request.db.settings.find_one()
    if not settings:
        settings = save_settings(request, defaults)
    for key in defaults.keys():
        if not key in settings:
            settings[key] = defaults[key]
    return settings


def save_settings(request, settings):
    request.db.settings.save(settings)
    return request.db.settings.find_one()


def includeme(config):
    settings = config.registry.settings

    logger.info('Add Settings')

    config.add_route('settings', '/settings')
    config.add_route('settings_auth', '/settings/auth')
    config.add_route('settings_ldap', '/settings/ldap')
    config.add_route('settings_github', '/settings/github')
    config.add_route('settings_esgf', '/settings/esgf')
    config.add_route('settings_solr', '/settings/solr/{tab}')

    # check if solr is activated
    def github_oauth(request):
        settings = request.registry.settings
        consumer_key = settings.get('github.consumer.key', '')
        consumer_secret = settings.get('github.consumer.secret', '')
        if len(consumer_key.strip()) < 20:
            # check database
            db = settings['db']
            entry = db.settings.find_one()
            if entry and 'github' in entry:
                consumer_key = entry['github']['consumer_key']
                consumer_secret = entry['github']['consumer_secret']
        return consumer_key, consumer_secret
    config.add_request_method(github_oauth, reify=True)
