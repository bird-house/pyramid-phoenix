
from pyramid.view import view_config
from pyramid.security import authenticated_userid
from .models import user_token
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
    token = user_token(request, user_id)
    
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
        {"type": "text", "text": "Parallel ID", "help":parallel_id_help,
            "id": "parallel_id", "value": "web1"},
        {"type": "text", "text": "Root path to the of check data",
            "id": "data_path", "value": EXAMPLEDATADIR},
        {"type": "select", "text": "Project", "id": "project",
            "value": "CORDEX", "allowed_values": ["CORDEX"] },
        {"type": "text", "text": "QC SELECT", "id": "select", "value": "", "help": qc_select_help},
        {"type": "text", "text": "QC LOCK", "id": "lock", "value": "", "help": qc_lock_help},
        {"type": "checkbox", "text": "Replica", "id": "replica", "value": ""},
        {"type": "checkbox", "text": "Latest", "id": "latest", "value": "", "checked": "checked"},
        {"type": "checkbox", "text": "Publish meta-data", "id": "publish_metadata", "value": "",
            "checked": "checked"},
        {"type": "checkbox", "text": "Publish quality-data", "id": "publish_quality",
            "value": "", "checked": "checked"},
        {"type": "checkbox", "text": "Clean afterwards", "id": "clean",
            "value": "", "help": "Removes the work data after the steps have finished"},
        ]
    html_fields = get_html_fields(fields)
    
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
        
