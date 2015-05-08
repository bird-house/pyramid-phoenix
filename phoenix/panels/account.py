from pyramid_layout.panel import panel_config

import logging
logger = logging.getLogger(__name__)

@panel_config(name='account_openid', renderer='phoenix:templates/panels/account_openid.pt')
def account_openid(context, request):
    return {}

@panel_config(name='account_esgf', renderer='phoenix:templates/panels/account_esgf.pt')
def account_esgf(context, request):
    return {}
