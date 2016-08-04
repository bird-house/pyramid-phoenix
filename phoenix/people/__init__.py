import logging
logger = logging.getLogger(__name__)


def includeme(config):
    # settings = config.registry.settings

    logger.debug('Adding profile ...')

    config.add_route('profile', 'people/profile/{tab}')
    config.add_route('forget_esgf_certs', 'people/forget_esgf_certs')
    config.add_route('generate_twitcher_token', 'people/gentoken')
