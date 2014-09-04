import pytz

def localize_datetime(dt, tz_name):
    """Provide a timzeone-aware object for a given datetime and timezone name
    """
    assert dt.tzinfo == None
    utc = pytz.timezone('UTC')
    aware = utc.localize(dt)
    timezone = pytz.timezone(tz_name)
    tz_aware_dt = aware.astimezone(timezone)
    return tz_aware_dt
