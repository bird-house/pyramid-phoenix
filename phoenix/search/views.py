from pyramid.view import view_config

import yaml

import pathlib
INDEX_PATH = pathlib.Path(__file__).parent.resolve() / "index"


@view_config(route_name='search', renderer='json', request_method="GET", xhr=True, accept="application/json")
def search(request):
    try:
        process_id = request.matchdict.get('process_id')
        value = request.matchdict.get('value')
        data = {"success": True}
        index = yaml.safe_load(open(INDEX_PATH / f"{process_id}.json"))
        data["items"] = index[value]
    except:
        data = {"success": False}
    return data