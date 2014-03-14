
import logging
logger = logging.getLogger(__name__)
from pyramid.view import view_config
from pyramid.security import authenticated_userid
from .models import user_token
from pyramid.httpexceptions import HTTPFound
import os
#TODO: Put constants into a config file
QCDIR = "/home/tk/sandbox/climdaps/var/qc_cache"
EXAMPLEDATADIR = "/home/tk/sandbox/climdaps/examples/data/CORDEX"
@view_config(route_name='qc_wizard',
             renderer='templates/qc_wizard.pt',
             layout='default',
             permission='edit',
             )
def qc_wizard(request):
    title = "Quality Control Wizard"
    user_id = authenticated_userid(request)
    #token = user_token(request, user_id)
    
    parallel_id_help = ("An identifier used to avoid processes running on the same directory." + 
                        " Using an existing one will remove all data inside its work directory.")
    parallel_ids = get_parallel_ids(user_id)
    if parallel_ids == []:
        parallel_id_help += " There are currently no existing Parallel IDs."
    else:
        parallel_id_help += " The existing Parallel IDs are:<br>" +", ".join(parallel_ids)
    qc_select_help = ("Comma separated list of parts of the path. If at least one of the elements " +
                      "in the list matches with a path in the data directory, its nc files are " + 
                      "added to the check. It is recommended to put variables into '/' to avoid " +
                      "accidental matches with other path elements. The first element of the path " + 
                      "does not start with a '/' and the last element does not end with a '/'. The " +
                      "wildcard '.*' should be used with care, as the handling of '/' is " + 
                      "considered undefined. (Assuming the paths exist a valid example is: " +
                      "AFR-44/.*/tas, EUR.*, /fx/)")
    qc_lock_help = ("Works similar to select, but prevents the given paths being added. " +
                    "Lock is stronger than select. (e.g. select tas and lock AFR-44 checks all "+
                    "tas that are not in AFR-44.)")

    #a field in fields must contain text, id and value. The entry help is optional.
    #allowed_values can be used if a limited number of possibile values should be available.
    #In that case value will be used as default if it is in allowed_values.
    #For type "checkbox" the existence of the "checked" key will lead to the checkbox being True.
    fields = [
        {"id": "parallel_id", "type": "text", "text": "Parallel ID", "help":parallel_id_help,
            "value": "web1"},
        {"id": "data_path", "type": "text", "text": "Root path to the of check data",
            "value": EXAMPLEDATADIR},
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
        #Create a restflow workflow (without writing it to a file).
        #The values are gathered in the yaml workflow_description generation method
        workflow_description = _create_qc_workflow(DATA)
        
        #Create a wps call for org.malleefowl.restflow
        ###identifier = 'org.malleefowl.restflow'
        ###inputs = [("workflow_description", str(workflow_description))]
        ###outputs = [("output",True), ("work_output", False), ("work_status", False)]
        ###execution = wps.execute(identifier, inputs=inputs, output=outputs)
        ###add_job(
        ###    request = request,
        ###    user_id = authenticated_userid(request),
        ###    identifier = identifier,
        ###    wps_url = wps.url,
        ###    execution = execution,
        ###    notes = states[5].get('info_notes', ''),
        ###    tags = states[5].get('info_tags', ''))


        return HTTPFound(location=request.route_url('jobs'))
    
    return {
            "title": title,
            "html_fields" : html_fields,
            }

def get_parallel_ids(user_id): 
    #If the file path is invalid an empty list is returned.
    path = os.path.join(QCDIR, user_id)
    history_fn = os.path.join(path, "parallel_id.history")
    history = []
    if os.path.isfile(history_fn):
        with open(history_fn, "r") as hist:
            lines = hist.readlines()
            for line in lines:
                history.append(line.rstrip("\n"))  
    existing_history = [x for x in history if os.path.isdir(os.path.join(path, x))] 
    return existing_history

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
        
def _create_qc_workflow(DATA):
    parallel_id = DATA["parallel_id"]
    data_path = DATA["data_path"]
    project =  DATA["project"]
    select = DATA["select"]
    lock = DATA["lock"]
    replica = "replica" in DATA
    latest = "latest" in DATA
    publish_metadata = "publish_metadata" in DATA
    publish_quality = "publish_quality" in DATA
    clean = "clean" in DATA
    yaml_document = ["---"]

