import logging
logger = logging.getLogger(__name__)


def includeme(config):
    # settings = config.registry.settings

    logger.debug('Adding people ...')

    config.add_route('people', 'people')
    config.add_route('delete_user', 'people/delete/{userid}')
    config.add_route('profile', 'people/profile/{userid}/{tab}')
    config.add_route('forget_esgf_certs', 'people/forget_esgf_certs')
    config.add_route('generate_twitcher_token', 'people/gentoken')
