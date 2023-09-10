from pyramid.view import view_config
from owslib.wps import WebProcessingService

import yaml
import json
import html

import pathlib
INDEX_PATH = pathlib.Path(__file__).parent.resolve() / "index"


@view_config(route_name='search', renderer='json', request_method="GET", xhr=True, accept="application/json")
def search(request):
    try:
        service_id = request.matchdict.get('service_id')
        process_id = request.matchdict.get('process_id')
        value = request.matchdict.get('value')
        data = {"success": True}
        index = yaml.safe_load(open(INDEX_PATH / f"{process_id}.json"))
        # update_from_remote_index(request, service_id, process_id)
        data["items"] = index[value]
    except Exception as e:
        data = {"success": False}
        # raise
    return data

def update_from_remote_index(request, service_id, process_id):
    remote_data = wps_metadata(request, service_id, process_id)
    if remote_data:
        pass


def wps_metadata(request, service_id, process_id):
    service = request.catalog.get_record_by_id(service_id)
    wps = WebProcessingService(url=service.url, verify=False)
    for process in wps.processes:
        if process.identifier == process_id:
            for metadata in process.metadata:
                if metadata.role == "https://clint.dkrz.de/spec/crai/info":
                    return parse_metadata(metadata.url)
    return None

def parse_metadata(data):
    # Replace HTML-encoded characters
    decoded_string = html.unescape(data)
    # Parse as json
    json_data = json.loads(decoded_string)
    return json_data


# def etienne():
#     import yaml
#     import pandas as pd
#     info_models = list(yaml.safe_load(craimodels.raw_text()).values())
#     df_models = pd.json_normalize(info_models, record_path=None, meta="dataset_name")