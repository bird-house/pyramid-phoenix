from pyramid.view import view_config


PROCESSES = {
    'crai': {
        'HadCRUT4': {
            'dataset_name': "HadCRUT4",
            'dataset_name_tooltip': "HadCRUT4 Training dataset: 82133 samples of near surface temperature anomalies"
                                    " from the 20th century reanalysis dataset (https://psl.noaa.gov/data/20thC_Rean/)"
                                    " spanning the period 1870-2009."
                                    " \nMask dataset: masks of missing values extracted from the HadCRUT4 dataset for the period 1850-2014.",
            'file': "https://www.metoffice.gov.uk/hadobs/hadcrut4/data/current/gridded_fields/HadCRUT.4.6.0.0.median_netcdf.zip",
            'file_tooltip': "Enter a URL to your HadCRUT4 netcdf file.",
            'variable_name': "temperature_anomaly",
            'variable_name_tooltip': "temperature_anomaly",
        },
        'HadCRUT5': {
            'dataset_name': "HadCRUT5",
            'dataset_name_tooltip': "HadCRUT5 Training dataset: 82133 samples of near surface temperature anomalies"
                                    " from the 20th century reanalysis dataset (https://psl.noaa.gov/data/20thC_Rean/)"
                                    " spanning the period 1870-2009."
                                    " \nMask dataset: masks of missing values extracted from the HadCRUT4 dataset for the period 1850-2014.",
            'file': "https://www.metoffice.gov.uk/hadobs/hadcrut5/data/current/non-infilled/HadCRUT.5.0.1.0.anomalies.ensemble_mean.nc",
            'file_tooltip': "Enter a URL to your HadCRUT5 netcdf file.",
            'variable_name': "tas_mean",
            'variable_name_tooltip': "tas_mean",
        }
    }
}

@view_config(route_name='search', renderer='json', request_method="GET", xhr=True, accept="application/json")
def search(request):
    try:
        process_id = request.matchdict.get('process_id')
        value = request.matchdict.get('value')
        result = {"success": True}
        result["result"] = PROCESSES[process_id][value]
    except:
        result = {"success": False}
    return result