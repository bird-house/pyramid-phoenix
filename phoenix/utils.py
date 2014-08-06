
def localize_datetime(dt, tz_name):
    """Provide a timzeone-aware object for a given datetime and timezone name
    """
    import pytz
    assert dt.tzinfo == None
    utc = pytz.timezone('UTC')
    aware = utc.localize(dt)
    timezone = pytz.timezone(tz_name)
    tz_aware_dt = aware.astimezone(timezone)
    return tz_aware_dt

def wps_wget_url(wps_url, cert_url, file_url):
    req_url = "{wps_url}?" +\
    "request=Execute" +\
    "&service=WPS" +\
    "&version=1.0.0" +\
    "&identifier={identifier}" +\
    "&DataInputs={inputs}" +\
    "&RawDataOutput={outputs};mimeType=application/x-netcdf"

    import urllib
    url = req_url.format(
        wps_url=wps_url,
        identifier="esgf_wget", 
        inputs="credentials=%s;file_identifier=%s" % (urllib.quote(cert_url), urllib.quote(file_url)),
        outputs="output")
    print url  
    
    


