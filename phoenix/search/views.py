from pyramid.view import view_config

PROCESSES = {
    'crai': {
        'hadcrut4': {
            'dataset_name': "HadCRUT4",
            'dataset_name_tooltip': "",
            'file': "https://www.metoffice.gov.uk/hadobs/hadcrut4/data/current/gridded_fields/HadCRUT.4.6.0.0.median_netcdf.zip",
            'file_tooltip': "Enter a URL to your HadCRUT4 netcdf file.",
            'variable_name': "temperature_anomaly",
            'variable_name_tooltip': "temperature_anomaly",
        },
        'hadcrut5': {
            'dataset_name': "HadCRUT5",
            'dataset_name_tooltip': "",
            'file': "https://www.metoffice.gov.uk/hadobs/hadcrut5/data/current/non-infilled/HadCRUT.5.0.1.0.anomalies.ensemble_mean.nc",
            'file_tooltip': "Enter a URL to your HadCRUT5 netcdf file.",
            'variable_name': "tas_mean",
            'variable_name_tooltip': "tas_mean",
        }
    }
}

@view_config(route_name='search', renderer='json', request_method="GET", xhr=False, accept="application/json")
def search(request):
    try:
        process_id = request.matchdict.get('process_id')
        value = request.matchdict.get('value')
        result = {"success": True}
        result["result"] = PROCESSES[process_id][value]
    except:
        result = {"success": False}
    return result