from authomatic.providers import oauth2, openid

DEFAULTS = {
    'popup': True,
}

AUTHENTICATION = {
    'openid': {
        'class_': openid.OpenID,
    },
    
    'github': {
        'class_': oauth2.GitHub,
        'consumer_key': '#####',
        'consumer_secret': '#####',
        'access_headers': {'User-Agent': 'Awesome-Octocat-App'},
    },
}


# Concatenate the configs.
config = {}
config.update(AUTHENTICATION)
config['__defaults__'] = DEFAULTS

