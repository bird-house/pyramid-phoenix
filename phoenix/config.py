from authomatic.providers import oauth2, openid
import authomatic

DEFAULTS = {
    'popup': True,
}

AUTHENTICATION = {
    'openid': {
        'class_': openid.OpenID,
    },
}

OAUTH2 = {
    
    'github': {
        'class_': oauth2.GitHub,
        'consumer_key': '#####',
        'consumer_secret': '#####',
        'access_headers': {'User-Agent': 'Awesome-Octocat-App'},
    },
}


# Concatenate the configs.
config = {}
config.update(OAUTH2)
config.update(AUTHENTICATION)
config['__defaults__'] = DEFAULTS

