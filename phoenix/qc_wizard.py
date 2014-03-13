
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
    #a field in fields must contain text, id and value. The entry help is optional.
    #options can be used if a limited number of possibile values should be available.
    #In that case value will be used as default if it is in options.
    fields = [
        {"text": "Parallel ID", "help":parallel_id_help, "id": "parallel_id", "value": "web1"},
        {"text": "Root path to the of check data", "id": "data_path", "value": EXAMPLEDATADIR},
        {"text": "Project", "id": "project", "value": "CORDEX", "options": ["CORDEX"] },
        ]
    
    return {
            "title": title,
            "fields" : fields,
            }

def get_parallel_ids(user_id): 
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
