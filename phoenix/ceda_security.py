from sqlalchemy import create_engine

import logging
LOGGER = logging.getLogger("PHOENIX")


PROCESS_ROLE_MAPPING = {
    "GetWeatherStations": ["surface"],
    "ExtractUKStationData": ["surface"],
}


def check_ceda_permissions(request, user, processid):
    """
    Check if the user has permission to access the process.
    """
    if user is None:
        # the user is not logged in so we cannot check
        return False

    if processid not in PROCESS_ROLE_MAPPING.keys():
        # the process is not a protected CEDA process
        return True

    users_roles = _get_user_roles(request, user.get("login_id"))

    for role in users_roles:
        if role in PROCESS_ROLE_MAPPING[processid]:
            return True

    return False


def _get_user_roles(request, user_id):
    """
    Call out to the DB to get the users rolls.
    """
    connection_credentials = request.registry.settings.get("ceda.db.creds")
    engine = create_engine(connection_credentials)

    with engine.connect() as conn:
        # Get userkey first
        query = f"select userkey from tbusers where accountid='{user_id}';"
        userkey = _get_response(conn, query, get_one=True)
        # Get all roles
        userkey = int(userkey)
        query = f"select datasetid from tbdatasetjoin where userkey = {userkey} and removed != 0;"
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
