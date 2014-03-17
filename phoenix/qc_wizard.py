
import logging
logger = logging.getLogger(__name__)
from pyramid.view import view_config
from pyramid.security import authenticated_userid
from .models import user_token, add_job
from pyramid.httpexceptions import HTTPFound
from wps import get_wps
from .helpers import wps_url
import os
#TODO: Put constants into a config file
QCDIR = "/home/tk/sandbox/test/climdapssplit/malleefowl/var/qc_cache"
EXAMPLEDATADIR = "/home/tk/sandbox/test/climdapssplit/malleefowl/examples/data/CORDEX"
WPS_SERVICE = "http://localhost:8090/wps"
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

        wps = get_wps(wps_url(request))
        workflow_description = _create_qc_workflow(DATA, user_id, token, wps)

        identifier = 'org.malleefowl.restflow.run'
        inputs = [("workflow_description", str(workflow_description) )]
        outputs = [("output",True), ("work_output", False), ("work_status", False)]

        execution = wps.execute(identifier, inputs=inputs, output=outputs)

        add_job(
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
        
def _create_qc_workflow(DATA, user_id, token, wps):
    #substitute the @ to avoid complications. 
    user_id = user_id.replace("@","(at)")
    token = token
    parallel_id = DATA["parallel_id"]
    data_path = DATA["data_path"]
    project =  DATA["project"]
    #ensure lock and select are valid values.
    select = DATA["select"]
    if select == '<colander.null>' or select == None:
        select =  ""
    lock = DATA["lock"]
    if lock == '<colander.null>' or lock == None:
        lock =  ""
    replica = "replica" in DATA
    latest = "latest" in DATA
    publish_metadata = "publish_metadata" in DATA
    publish_quality = "publish_quality" in DATA
    clean = "clean" in DATA

    wps_address = wps.url
    #generated variables
    #document
    yaml_document = [
        "---",
        "",
        "imports:",
        "- classpath:/common/directors.yaml",
        "- classpath:/common/groovy/actors.yaml",
        "components:",
        "- id: QCProcesses",
        "  type: Workflow",
        "  properties:",
        "    director: !ref MTDataDrivenDirector",
        "    nodes:",
        "    - !ref InputGenerator",
        "    - !ref QC_Init",
        "    - !ref QC_Check",
        "",
        "- id: InputGenerator",
        "  type: GroovyActorNode",
        "  properties:",
        "    actor.step: | ",
        '      run = "run"',
        "    outflows:",
        "      run: /variable/init_run/",
        "",
        "- id: WpsExecute",
        "  type: GroovyActor",
        "  properties:",
        "    step: |",
        "      tempFile = File.createTempFile('wps-result-', '.json', new File('.'))",
        "      outfile = tempFile.absolutePath",
        "      cmd = ['wpsclient', 'execute', ",
        "                    '-s', service,",
        "                    '-i', identifier,",
        "                    '-o', outfile]",
        "      if (verbose) {",
        "          cmd.add('-v')",
        "      }",
        "      for (item in sources) {",
        "          cmd.add('--input')",
        "          cmd.add('file_identifier=' + item.value)",
        "      }",
        "      for (item in input) {",
        "          cmd.add('--input')",
        "          cmd.add('' + item.value)",
        "      }",
        "      for (item in output) {",
        "          cmd.add('--output')",
        "          cmd.add('' + item.value)",
        "      }",
        "     ",
        "      proc = cmd.execute()",
        "      proc.waitFor()",
        "      result = identifier + ' ... failed'",
        "      status = result",
        "      import org.yaml.snakeyaml.Yaml",
        "      resultFile = new File(outfile)",
        "      if (resultFile.exists()) {",
        "         yaml = new Yaml()",
        "         wpsResult = yaml.load(new FileInputStream(resultFile))",
        "     ",
        "         for (item in wpsResult) {",
        "            result = item.reference",
        "            status = identifier + ' ... done'",
        "         }",
        "      }",
        "      finished = run",
        "    inputs:",
        "      run:",
        "      identifier: ",
        "      service:",
        "      input:",
        "        type: Collection",
        "        optional: true",
        "        nullable: true",
        "      output:",
        "        type: Collection",
        "        optional: true",
        "        nullable: true",
        "      sources:",
        "        type: Collection",
        "        optional: true",
        "        nullable: true",
        "      verbose:",
        "        type: Bool",
        "    outputs:",
        "      result:",
        "      status:",
        "      finished:",
        "",
        "- id: QC_Init",
        "  type: Node",
        "  properties:",
        "    actor: !ref WpsExecute",
        "    constants:",
        "      service: " + wps_address,
        "      identifier: QC_Init_User",
        "      input: " + ('["parallel_id=' + parallel_id + '", "username=' + user_id +
                           '", "token=' + token + '", "data_path=' + data_path + '"]'),
        "      output: [('output',True)]",
        "    inflows:",
        "      run: /variable/init_run/",
        "    outflows:",
        "      finished: /variable/init_finished/",
        "",
        "- id: QC_Check",
        "  type: Node",
        "  properties:",
        "    actor: !ref WpsExecute",
        "    constants:",
        "      service: " + wps_address,
        "      identifier: QC_Check_User",
        "      input: " + ('["parallel_id=' + parallel_id + '", "username=' + user_id + 
                           '", "token=' + token + '", "project=' + project)]
    if select != "":
        yaml_document[-1] += '", "select=' + select 
    if lock != "":
        yaml_document[-1] += '", "lock=' + lock 
    yaml_document[-1] += '"]'
    yaml_document += [
        "      output: []",
        "    inflows:",
        "      run : /variable/init_finished/",
        "    outflows:",
        "      finished: /variable/check_finished/",
       ]
    document = "\n".join(yaml_document)+"\n"
    with open("/home/tk/sandbox/log","w") as f:
        f.write(document)
    return document
