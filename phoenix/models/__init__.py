import uuid
import datetime

from phoenix import utils

import logging
logger = logging.getLogger(__name__)

def user_email(request):
    from pyramid.security import authenticated_userid
    return authenticated_userid(request)

def get_user(request, email=None):
    if email is None:
        email = user_email(request)
    return request.db.users.find_one(dict(email=email))

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
        created = datetime.datetime.now(),
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
        source=csw.records[rec].source
        # TODO: fix owslib url handling and wps caps url
        #if not '?' in source.lower():
        #    source = utils.build_url(source, [('service', 'WPS'), ('version', '1.0.0'), ('request', 'GetCapabilities')])
        
        items.append(dict(
            identifier=csw.records[rec].identifier,
            title=csw.records[rec].title,
            subjects=csw.records[rec].subjects,
            abstract=csw.records[rec].abstract,
            references=csw.records[rec].references,
            format=csw.records[rec].format,
            source=source,
            rights=csw.records[rec].rights))
    return items

def collect_outputs(status_location, prefix="job"):
    from owslib.wps import WPSExecution
    execution = WPSExecution()
    execution.checkStatus(url=status_location, sleepSecs=0)
    outputs = {}
    for output in execution.processOutputs:
        oid = "%s.%s" %(prefix, output.identifier)
        outputs[oid] = output
    return outputs

def process_outputs(request, jobid, tab='outputs'):
    job = request.db.jobs.find_one({'identifier': jobid})
    outputs = {}
    # TODO: dirty hack for workflows ... not save and needs refactoring
    from owslib.wps import WPSExecution
    execution = WPSExecution()
    execution.checkStatus(url=job['status_location'], sleepSecs=0)
    if job['workflow']:
        import urllib
        import json
        wf_result_url = execution.processOutputs[0].reference
        wf_result_json = json.load(urllib.urlopen(wf_result_url))
        count = 0
        if tab == 'outputs':
            for url in wf_result_json.get('worker', []):
                count = count + 1
                outputs = collect_outputs(url, prefix='worker%d' % count )
        elif tab == 'resources':
            for url in wf_result_json.get('source', []):
                count = count + 1
                outputs = collect_outputs(url, prefix='source%d' % count )
        elif tab == 'inputs':
            outputs = {}
    elif tab == 'outputs':
        outputs = collect_outputs(job['status_location'])
    return outputs

def job_details(request, jobid):
    job = request.db.jobs.find_one({'identifier': jobid})
    details = {}
    details['title'] = job.get('title')
    details['description'] = job.get('abstract')
    details['status'] = job.get('status')
    details['status_location'] = job.get('status_location')
    details['message'] = job.get('message')
    details['duration'] = job.get('duration')
    details['finished'] = job.get('finished')
    details['progress'] = job.get('progress')
    return details
