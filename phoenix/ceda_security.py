import json

from sqlalchemy import create_engine

import logging
LOGGER = logging.getLogger("PHOENIX")


CEDA_ROLE_MAP_CONFIG = "/usr/local/birdhouse/etc/phoenix/ceda_process_role_map.json"


def check_ceda_permissions(request, user, processid):
    """
    Check if the user has permission to access the process.
    Return a boolean:
     - True:  allow access
     - False: deny access
    """
    role_mappings = _get_process_role_mappings()
    restricted_procs = role_mappings["restricted_by_role"]

    if processid in role_mappings.get("open", []):
        # If open, everyone can access
        return True

    if user is None or user.get("login_id") in role_mappings["suspended_users"]:
        # the user is not logged or is suspended so we return False
        return False

    if processid in role_mappings.get("restricted_to_ceda_users", []):
        # the process is available to all CEDA users
        return True

    if user.get("login_id") in role_mappings["restricted_by_user_id"].get(processid, []):
        # the process is available to this specific user
        return True

    users_roles = _get_user_roles(request, user.get("login_id"))

    for role in users_roles:
        if role in restricted_procs.get(processid, []):
            return True

    return False


def _get_process_role_mappings():
    """
    Load the role mappings from the config file.
    """
    try:
        with open(CEDA_ROLE_MAP_CONFIG) as reader:
           return json.load(reader)
    except Exception:
        # If cannot read it, set defaults
        return {"restricted_by_role": {}, "restricted_to_ceda_users": [], 
                "open": [], "suspended_users": [], "restricted_by_user_id": {}}


def _get_user_roles(request, user_id):
    """
    Call out to the DB to get the users rolls.
    """
    connection_credentials = request.registry.settings.get("ceda.db.creds")
    engine = create_engine(connection_credentials)

    with engine.connect() as conn:
        query = request.registry.settings.get("ceda.db.query")
        query = query.replace("{user_id}", user_id)
        roles = set(_get_response(conn, query))
        roles = sorted(
            [r for r in roles if not r.startswith("gws_") and not r.startswith("vm_")]
        )

    return roles


def _get_response(conn, query, get_one=False):
    rs = conn.execute(query)
    results = [item[0] for item in rs]
    if get_one:
        results = results[0]
    return results
