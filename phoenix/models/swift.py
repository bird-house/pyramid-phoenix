from swiftclient import client, ClientException
from pyramid.security import authenticated_userid

import logging
logger = logging.getLogger(__name__)

def swift_upload(request, storage_url, auth_token, container, prefix, source):
    inputs = []
    inputs.append( ('storage_url', storage_url.encode('ascii', 'ignore')) )
    inputs.append( ('auth_token', auth_token.encode('ascii', 'ignore')) )
    inputs.append( ('container', container.encode('ascii', 'ignore')) )
    inputs.append( ('prefix', prefix.encode('ascii', 'ignore')) )
    inputs.append( ('resource', source.encode('ascii', 'ignore')) )

    from phoenix.tasks import execute
    execute.delay(
        userid=authenticated_userid(request),
        url=request.wps.url,
        identifier='swift_upload',
        inputs=inputs,
        output=[('output',True)])

def swift_login(request, username, password):
    storage_url = auth_token = None

    settings = request.registry.settings
    auth_url = settings.get('swift.auth.url')
    auth_version = int(settings.get('swith.auth.version', 1))
    logger.debug('auth_url = %s', auth_url)

    try:
        (storage_url, auth_token) = client.get_auth(auth_url, username, password, auth_version=auth_version)
    except ClientException:
        raise Exception('swift login failed for user %s' % username)
    return dict(storage_url=storage_url, auth_token=auth_token)

def get_containers(storage_url, auth_token):
    containers = []
    try:
        account_stat, containers = client.get_account(storage_url, auth_token)
    except ClientException as exc:
        logger.exception("Could not get containers")
        if exc.http_status == 403:
            logger.warn("Container listing failed")
    return containers

def get_objects(storage_url, auth_token, container, prefix=None):
    objects = []
    
    try:
        meta, objects = client.get_container(storage_url, auth_token,
                                             container,
                                             delimiter='/',
                                             prefix=prefix)
        # filter directory
        for obj in objects:
            if obj.get('content_type') in ('application/directory', 'application/x-directory'):
                objects.remove(obj)
    except ClientException:
        logger.exception("Access denied.")
    return objects

def prefix_list(prefix):
    prefixes = []

    if prefix:
        elements = prefix.split('/')
        elements = filter(None, elements)
        prefix = ""
        for element in elements:
            prefix += element + '/'
            prefixes.append({'display_name': element, 'full_name': prefix})

    return prefixes

    
