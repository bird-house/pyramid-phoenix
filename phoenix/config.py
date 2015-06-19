from authomatic.providers import oauth2, openid
import authomatic


def update_config(request):

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
            'consumer_key': request.registry.settings.get('github.consumer.key'),
            'consumer_secret': request.registry.settings.get('github.consumer.secret'),
            'access_headers': {'User-Agent': 'Phoenix'},
        },
    }


    # Concatenate the configs.
    config = {}
    config.update(OAUTH2)
    config.update(AUTHENTICATION)
    config['__defaults__'] = DEFAULTS
    return config

