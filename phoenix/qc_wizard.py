import logging
logger = logging.getLogger(__name__)
from pyramid.view import view_config
from pyramid.security import authenticated_userid
import models
from pyramid.httpexceptions import HTTPFound
from owslib.wps import WebProcessingService
import os

DEFAULTQUALITYSERVER="http://suffolk.dkrz.de:8094/wps"

@view_config(route_name='qc_wizard_check',
             renderer='templates/qc_wizard.pt',
             layout='default',
             permission='edit',
             )
def qc_wizard_check(request):
    title = "Quality Control Wizard"
    user_id = authenticated_userid(request)
    token = "1234"# user_token(request, user_id)
    if not token:
        raise Exception("Can not find token")
    
    session_id_help = ("An identifier used to avoid processes running on the same directory." + 
                        " Using an existing one will remove all data inside its directory.")
    session_ids = get_session_ids(user_id, request)
    if session_ids == []:
        session_id_help += " There are currently no existing Session IDs."
    else:
        session_id_help += " The existing Session IDs are:<br>" +", ".join(session_ids)
    qc_select_help = ("Comma separated list of parts of the path descriptions." +
                      " If at least one description in the list matches the path is included." + 
                      " In the path description '.*' is for any character sequence. (e.g. " +
                      "AFR-44/.*/tas, EUR.*, /fx/)")
    qc_lock_help = ("Works similar to select, but prevents the given paths being added. " +
                    "Lock is stronger than select. (e.g. select tas and lock AFR-44 checks all "+
                    "paths with tas that do not contain AFR-44.)")

    #a field in fields must contain text, id and value. The entry help is optional.
    #allowed_values can be used if a limited number of possibile values should be available.
    #In that case value will be used as default if it is in allowed_values.
    #For type "checkbox" the existence of the "checked" key will lead to the checkbox being True.
    fields = [
        {"id": "quality_server_address", "type" : "text", "text": "URL to the Quality WPS",
         "value":DEFAULTQUALITYSERVER},
        {"id": "session_id", "type": "text", "text": "Session ID", "help":session_id_help,
            "value": "web1"},
        #{"id": "irods_home", "type": "text", "text": "iRods Home",
        #    "help": "The home directory of iRods", "value":"qc_dummy_DKRZ"},
        #{"id": "irods_collection", "type": "text", "text": "iRods collection", 
        #    "help": "Name of the to analyze collection", "value": "qc_test_20140416"},
        {"id": "data_path", "type": "text", "text": "Root path of the to check data",
            "value": ""},
        {"id": "project", "type": "select", "text": "Project", 
            "value": "CORDEX", "allowed_values": ["CORDEX"] },
        {"id": "select", "type": "text", "text": "QC SELECT", "value": "", "help": qc_select_help},
        {"id": "lock", "type": "text", "text": "QC LOCK", "value": "", "help": qc_lock_help},
        {"id": "replica", "type": "checkbox", "text": "Replica", "value": ""},
        {"id": "latest", "type": "checkbox", "text": "Latest", "value": "", "checked": "checked"},
        {"id": "publish_metadata", "type": "checkbox", "text": "Publish meta-data",  "value": "",
            "checked": "checked"},
        {"id": "publish_quality", "type": "checkbox", "text": "Publish quality-data", 
            "value": "", "checked": "checked"},
        {"id": "clean", "type": "checkbox", "text": "Clean afterwards", 
            "value": "", "help": "Removes the work data after the steps have finished"},
        ]
    html_fields = get_html_fields(fields)

    if "submit" in request.POST:
        DATA = request.POST
        #shorten the method parameters by automatically insert DATA
        def getValue(identifier):
            return getValueStatic(DATA, identifier)
        def getBool(identifier):
            return getBoolStatic(DATA, identifier)
        ##########################
        #collect input parameters#
        ##########################
        wps_address = getValue("quality_server_address")
        username = str(user_id.replace("@","(at)"))
        token = token
        session_id = getValue("session_id")
        #irods_home = DATA["irods_home"]
        #irods_collection = DATA["irods_collection"]
        data_path = getValue("data_path")
        project =  getValue("project")
        #ensure lock and select are valid values.
        select = getValue("select")
        lock = getValue("lock")
        #html checkboxes are true if and only if they are in the POST (DATA variable)
        replica = getBool("replica")
        latest = getBool("latest")
        publish_metadata = getBool("publish_metadata")
        publish_quality = getBool("publish_quality")
        cleanup = getBool("clean")
        #####################
        #Run the wps call#
        #####################
        wps = WebProcessingService(wps_address)
        identifier = "QC_Check_Full"
        inputs = [("username", username), ("token", token), ("session_id", session_id),
                  #("irods_home", irods_home), ("irods_collection", irods_collection),
                  ("data_path", data_path),
                  ("project", project), 
                  ("select", select), ("lock", lock),
                  ("replica", replica), ("latest", latest), ("publish_metadata", publish_metadata),
                  ("publish_quality", publish_quality), ("cleanup", cleanup)]
        #filter empty string values, because wps.execute does not like them.
        inputs = [(x,y) for (x,y) in inputs if y!=""]
         
        outputs = [("process_log", True)]
        execution = wps.execute(identifier, inputs=inputs, output=outputs)
        models.add_job(
            request = request,
            wps_url = execution.serviceInstance,
            status_location = execution.statusLocation,
            notes = "test",
            tags = "test")

        return HTTPFound(location=request.route_url('jobs'))
    
    return {
            "title": title,
            "html_fields" : html_fields,
            }

def get_session_ids(user_id, request): 
    service_url = request.wps.url
    token = "1234"#user_token(request, user_id)
    identifier = 'Get_Session_IDs'
    inputs = [("username",user_id.replace("@","(at)")),("token",token)]
    outputs = "session_ids"
    from wps import execute
    wpscall_result = execute(service_url, identifier, inputs=inputs, output=outputs)
    #there is only 1 output therefore index 0 is used for session_ids
    if len(wpscall_result) > 0:
        session_ids = wpscall_result[0].split("/")
    else:
        session_ids = []
    return session_ids

def get_html_fields(fields):
    """
    Converts a fields table with mandatory keywords type, text, id and partially optional 
    keywords value, allowed_values, checked and help into html input lines.

    The tal in the templates has become too complicated therefore the python code handles
    most of the conditions.
    """
    html_fields = []
    for field in fields:
        html_field = {}
        for key in ["help","text","id"]:
            if key in field:
                html_field[key] = field[key]
        if field["type"] == "text":
            html_field["input_html"] = ("<input name=\"" + field["id"] + "\" value=\"" + 
                                        field["value"] + "\" id=\"" + field["id"] + 
                                        "\"type=\"text\">\n")

        if field["type"] == "select":
            html_field["input_html"] = ("<select name=\"" + field["id"] + "\" value=\"" + 
                                        field["value"] + "\">\n")
            for option in field["allowed_values"]:
                html_field["input_html"] += "<option>"+option+"</option>\n"
            html_field["input_html"] += "</select>\n"

        if field["type"] == "checkbox":
            html_field["input_html"] = ("<input name=\"" + field["id"] + "\" value=\"" + 
                                        field["value"] + "\" id=\"" + field["id"] + 
                                        "\"type=\"checkbox\"")
            if "checked" in field:
                html_field["input_html"] += " checked=\"checked\""
            html_field["input_html"] += ">\n"
        html_fields.append(html_field)
    return html_fields


@view_config(route_name='qc_wizard_yaml',
             renderer='templates/qc_wizard.pt',
             layout='default',
             permission='edit',
             )
def qc_wizard_yaml(request):
    title = "Quality Control Wizard"
    user_id = authenticated_userid(request)
    token = "1234" # user_token(request, user_id)
    
    session_id_help = ("An identifier used to avoid processes running on the same directory." + 
                        " Using an existing one will remove all data inside its work directory.")
    session_ids = get_session_ids(user_id, request)
    if session_ids == []:
        session_id_help += " There are currently no existing Session IDs."
    else:
        session_id_help += " The existing Session IDs are:<br>" +", ".join(session_ids)
    yamllogs_help = "The comma separated list of logfile locations"
    oldprefix_help = "The data path in the provided logfiles"
    newprefix_help = "The data path on the machine"

    #a field in fields must contain text, id and value. The entry help is optional.
    #allowed_values can be used if a limited number of possibile values should be available.
    #In that case value will be used as default if it is in allowed_values.
    #For type "checkbox" the existence of the "checked" key will lead to the checkbox being True.
    fields = [
        {"id": "quality_server_address", "type" : "text", "text": "URL to the Quality WPS",
         "value":DEFAULTQUALITYSERVER},
        {"id": "session_id", "type": "text", "text": "Session ID", "help":session_id_help,
            "value": "checkdone"},
        {"id": "yamllogs", "type": "text", "text": "YAML logs", "help": yamllogs_help, "value": ""},
        {"id": "prefix_old", "type": "text", "text": "Old prefix", "help": oldprefix_help, "value": ""},
        {"id": "prefix_new", "type": "text", "text": "New prefix", "help": newprefix_help, "value": ""},
        {"id": "project", "type": "select", "text": "Project", 
            "value": "CORDEX", "allowed_values": ["CORDEX"] },
        {"id": "replica", "type": "checkbox", "text": "Replica", "value": ""},
        {"id": "latest", "type": "checkbox", "text": "Latest", "value": "", "checked": "checked"},
        {"id": "publish_metadata", "type": "checkbox", "text": "Publish meta-data",  "value": "",
            "checked": "checked"},
        {"id": "publish_quality", "type": "checkbox", "text": "Publish quality-data", 
            "value": "", "checked": "checked"},
        {"id": "clean", "type": "checkbox", "text": "Clean afterwards", 
            "value": "", "help": "Removes the work data after the steps have finished"},
        ]
    html_fields = get_html_fields(fields)

    if "submit" in request.POST:
        DATA = request.POST
        #shorten the method parameters by automatically insert DATA
        def getValue(identifier):
            return getValueStatic(DATA, identifier)
        def getBool(identifier):
            return getBoolStatic(DATA, identifier)
        ##########################
        #collect input parameters#
        ##########################
        username = str(user_id.replace("@","(at)"))
        token = token
        session_id = getValue("session_id")
        yamllogs = getValue("yamllogs")
        prefix_old = getValue("prefix_old")
        prefix_new = getValue("prefix_new")
        project =  getValue("project")
        #html checkboxes are true if and only if they are in the POST (DATA variable)
        replica = getBool("replica")
        latest = getBool("latest")
        publish_metadata = getBool("publish_metadata")
        publish_quality = getBool("publish_quality")
        cleanup = getBool("clean")

        wps_address = getValue("quality_server_address")
        wps = WebProcessingService(wps_address)
        
        ##################
        #Run the wps call#
        ##################
        wps = request.wps
        identifier = "QC_Check_YAML"
        inputs = [("username", username), ("token", token), ("session_id", session_id),
                  ("yamllogs", yamllogs), ("prefix_old", prefix_old), ("prefix_new", prefix_new),
                  ("project", project), 
                  ("replica", replica), ("latest", latest), ("publish_metadata", publish_metadata),
                  ("publish_quality", publish_quality), ("cleanup", cleanup)]

        outputs = [("process_log", True)]
        #wps.execute does not like empty strings as value, so filter it out
        inputs = [(x,y) for (x,y) in inputs if y!=""]

        g = open("/home/dkrz/k204205/log","w")
        g.write(str(inputs)+"\n")
        g.write(str(outputs)+"\n")
        g.write(str(identifier)+"\n")
        g.flush()
        execution = wps.execute(identifier, inputs=inputs, output=outputs)

        models.add_job(
            request = request,
            user_id = authenticated_userid(request),
            identifier = identifier,
            wps_url = wps.url,
            execution = execution,
            notes = "test",
            tags = "test")

        return HTTPFound(location=request.route_url('jobs'))
    
    return {
            "title": title,
            "html_fields" : html_fields,
            }

################
#HELPER METHODS#
################
def getValueStatic(DATA, identifier):
    val = DATA.get(identifier, "")
    if str(val) in ["<colander.null>", "None"]:
        val = ""
    return str(val)
def getBoolStatic(DATA, identifier):
    return str(identifier in DATA).lower()
