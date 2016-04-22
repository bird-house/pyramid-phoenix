import logging
logger = logging.getLogger(__name__)

def includeme(config):
    settings = config.registry.settings

    logger.info('Adding profile ...')

    config.add_route('profile', '/profile/{tab}')
    config.add_route('forget_esgf_certs', '/forget_esgf_certs')
    config.add_route('generate_twitcher_token', '/generate_twitcher_token')
