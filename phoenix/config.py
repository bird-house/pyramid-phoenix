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
            'id': authomatic.provider_id(),
            'scope': oauth2.GitHub.user_info_scope,
            '_apis': {
                'Get your events': ('GET', 'https://api.github.com/users/{user.username}/events'),
                'Get your watched repos': ('GET', 'https://api.github.com/user/subscriptions'),
            },
        },
    }


    # Concatenate the configs.
    config = {}
    config.update(OAUTH2)
    config.update(AUTHENTICATION)
    config['__defaults__'] = DEFAULTS
    return config

