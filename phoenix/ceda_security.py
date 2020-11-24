import logging
LOGGER = logging.getLogger("PHOENIX")


PROCESS_ROLE_MAPPING = {
    "GetWeatherStations": ["surface"],
    "ExtractUKStationData": ["surface"]
    }


def check_ceda_permissions(user, processid):
    if user is None:
        # the user is not logged in so we cannot check
        return False

    if processid not in PROCESS_ROLE_MAPPING.keys():
        # the process is not a protected CEDA process
        return True

    users_roles = _get_user_roles(user.get("login_id"))

    for role in users_roles:
        if role in PROCESS_ROLE_MAPPING[processid]:
            return True

    return False


def _get_user_roles(login_id):
    # add database lookup here
    return ["surface", "top"]
