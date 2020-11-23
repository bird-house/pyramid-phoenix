import logging
LOGGER = logging.getLogger("PHOENIX")


def check_ceda_permissions(user, processid):
    if user is None:
        # the user is not logged in so we cannot check
        return False

    login_id = user.get("login_id")

    if processid == "GetWeatherStations":
        return _check_get_weather_stations(login_id)
    elif processid == "ExtractUKStationData":
        return _check_extract_UK_station_data(login_id)

    # the process is not a protected CEDA process
    return True


def _check_get_weather_stations(login_id):
    if login_id == "user01":
        return True


def _check_extract_UK_station_data(login_id):
    if login_id == "user01":
        return False