import uuid
import datetime

from .exceptions import MyProxyLogonFailure

import logging
logger = logging.getLogger(__name__)

def query_esgf_files(latest=True, replica=False, distrib=True, **constraints):
    logger.debug('latest=%s, replica=%s, distrib=%s', latest, replica, distrib)
    logger.debug('constraints = %s', constraints)
    from pyesgf.search import SearchConnection
    # TODO: change esgf url
    conn = SearchConnection('http://localhost:8081/esg-search', distrib=distrib)
    fields = ['id', 'title', 'size', 'number_of_files', 'number_of_aggregations']
    ctx = conn.new_context(latest=latest, replica=replica, **constraints)
    logger.debug('datasets found %d', ctx.hit_count)
    result = []
    for ds in ctx.search():
        result.append(ds.json)
    #files = ds.file_context().search()
    #logger.debug('num files = %d', len(files))
    #for file in files:
    #    print file.download_url
    #    print file.filename
    #    print file.size
    return result

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

def myproxy_logon(request, openid, password):
    inputs = []
    inputs.append( ('openid', openid.encode('ascii', 'ignore')) )
    inputs.append( ('password', password.encode('ascii', 'ignore')) )

    logger.debug('update credentials with openid=%s', openid)

    execution = request.wps.execute(
        identifier='esgf_logon',
        inputs=inputs,
        output=[('output',True),('expires',False)])
    logger.debug('wps url=%s', execution.url)
    
    from owslib.wps import monitorExecution
    monitorExecution(execution)
    
    if not execution.isSucceded():
        raise MyProxyLogonFailure('logon process failed.',
                                  execution.status,
                                  execution.statusMessage)
    credentials = execution.processOutputs[0].reference
    cert_expires = execution.processOutputs[1].data[0]
    logger.debug('cert expires %s', cert_expires)
    return dict(credentials=credentials, cert_expires=cert_expires)

def cloud_logon(request, username, password):
    inputs = []
    inputs.append( ('username', username.encode('ascii', 'ignore')) )
    inputs.append( ('password', password.encode('ascii', 'ignore')) )

    execution = request.wps.execute(
        identifier='cloud_login',
        inputs=inputs,
        output=[('storage_url',False),('auth_token',False)])
    logger.debug('wps url=%s', execution.url)
    
    from owslib.wps import monitorExecution
    monitorExecution(execution)
    
    if not execution.isSucceded():
        raise Exception('logon process failed.',
                        execution.status,
                        execution.statusMessage)
    storage_url = execution.processOutputs[0].data[0]
    auth_token = execution.processOutputs[1].data[0]
    return dict(storage_url=storage_url, auth_token=auth_token)





    
