# -*- coding: utf-8 -*-
"""
Keys with leading underscore are our custom provider-specific data.
"""

from authomatic.providers import openid
import authomatic
#import copy

DEFAULT_MESSAGE = 'Have you got a bandage?'

SECRET = 'sdjfsi8sdfnfsdlfsdfsfsdkf8ueoruow'

DEFAULTS = {
    'popup': True,
}

AUTHENTICATION = {
    'openid': {
        'class_': openid.OpenID,
    },
}


# Concatenate the configs.
config = {}
config.update(AUTHENTICATION)
config['__defaults__'] = DEFAULTS

