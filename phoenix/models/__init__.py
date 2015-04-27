import uuid
import datetime

from swiftclient import client, ClientException

import logging
logger = logging.getLogger(__name__)

def add_user(
    request,
    email,
    openid='',
    name='unknown',
    organisation='unknown',
    notes='',
    activated=False):
    user=dict(
        identifier = uuid.uuid4().get_urn(),
        email = email,
        openid = openid,
        name = name,
        organisation = organisation,
        notes = notes,
        activated = activated,
        creation_time = datetime.datetime.now(),
        last_login = datetime.datetime.now())
    request.db.users.save(user)
    return request.db.users.find_one({'email':email})

def add_job(request, title, wps_url, status_location, workflow=False, abstract=None, keywords=None):
    from pyramid.security import authenticated_userid

    logger.debug("add job: status_location=%s", status_location)

    job = dict(
        # TODO: need job name ...
        #identifier = uuid.uuid4().get_urn(), # TODO: urn does not work as id in javascript
        identifier = uuid.uuid4().get_hex(),
        workflow = workflow,
        title = title,
        abstract = abstract,
        # TODO: keywords must be a list
        keywords = keywords,
        #TODO: dont use auth... userid=email ...
        email = authenticated_userid(request),
        wps_url = wps_url,
        status_location = status_location,
        creation_time = datetime.datetime.now(),
        is_complete = False)
    request.db.jobs.save(job)

def user_stats(request):
    num_unregistered = request.db.users.find({"activated": False}).count()
    
    d = datetime.datetime.now() - datetime.timedelta(hours=3)
    num_logins_3h = request.db.users.find({"last_login": {"$gt": d}}).count()

    d = datetime.datetime.now() - datetime.timedelta(days=7)
    num_logins_7d = request.db.users.find({"last_login": {"$gt": d}}).count()

    return dict(num_users=request.db.users.count(),
                num_unregistered=num_unregistered,
                num_logins_3h=num_logins_3h,
                num_logins_7d=num_logins_7d)

def get_wps_list(request):
    csw = request.csw
    csw.getrecords(
        qtype="service",
        esn="full",
        propertyname="dc:format",
        keywords=['WPS'])
    items = []
    for rec in csw.records:
        items.append(dict(
            identifier=csw.records[rec].identifier,
            title=csw.records[rec].title,
            subjects=csw.records[rec].subjects,
            abstract=csw.records[rec].abstract,
            references=csw.records[rec].references,
            format=csw.records[rec].format,
            source=csw.records[rec].source,
            rights=csw.records[rec].rights))
    return items

def swift_upload(request, storage_url, auth_token, container, prefix, source):
    inputs = []
    inputs.append( ('storage_url', storage_url.encode('ascii', 'ignore')) )
    inputs.append( ('auth_token', auth_token.encode('ascii', 'ignore')) )
    inputs.append( ('container', container.encode('ascii', 'ignore')) )
    inputs.append( ('prefix', prefix.encode('ascii', 'ignore')) )
    inputs.append( ('resource', source.encode('ascii', 'ignore')) )

    logger.debug("inputs = %s", inputs)

    execution = request.wps.execute(
        identifier='swift_upload',
        inputs=inputs,
        output=[('output',True)])
    
    from owslib.wps import monitorExecution
    monitorExecution(execution)
    
    if not execution.isSucceded():
        raise Exception('swift upload failed')

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

    
