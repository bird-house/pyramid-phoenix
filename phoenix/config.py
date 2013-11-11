from authomatic.providers import openid

CONFIG = {
    
    'openid': {
           
        # OpenID provider dependent on the python-openid package.
        'class_': openid.OpenID,
    }
}
