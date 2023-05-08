from pyramid.view import view_config


PROCESSES = {
    'crai': {
        'HadCRUT4': [
            {
                'name': 'dataset_name',
                'value': "HadCRUT4",
                'title': "HadCRUT4 Training dataset: 82133 samples of near surface temperature anomalies"
                         " from the 20th century reanalysis dataset (https://psl.noaa.gov/data/20thC_Rean/)"
                         " spanning the period 1870-2009."
                         " \nMask dataset: masks of missing values extracted from the HadCRUT4 dataset for the period 1850-2014.",
             
            },
            {
                'name': 'file',
                'value': "https://www.metoffice.gov.uk/hadobs/hadcrut4/data/current/gridded_fields/HadCRUT.4.6.0.0.median_netcdf.zip",
                'title': "Enter a URL to your HadCRUT4 netcdf file.",
            },
            {
                'name': 'variable_name',
                'value': "temperature_anomaly",
                'title': "temperature_anomaly",
            },
        ],
        'HadCRUT5': [
            {
                'name': 'dataset_name',
                'value': "HadCRUT5",
                'title': "HadCRUT5 Training dataset: 82133 samples of near surface temperature anomalies"
                         " from the 20th century reanalysis dataset (https://psl.noaa.gov/data/20thC_Rean/)"
                         " spanning the period 1870-2009."
                         " \nMask dataset: masks of missing values extracted from the HadCRUT4 dataset for the period 1850-2014.",
             
            },
            {
                'name': 'file',
                'value': "https://www.metoffice.gov.uk/hadobs/hadcrut5/data/current/non-infilled/HadCRUT.5.0.1.0.anomalies.ensemble_mean.nc",
                'title': "Enter a URL to your HadCRUT5 netcdf file.",
            },
            {
                'name': 'variable_name',
                'value': "tas_mean",
                'title': "tas_mean",
            },
        ],
    }
}

@view_config(route_name='search', renderer='json', request_method="GET", xhr=True, accept="application/json")
def search(request):
    try:
        process_id = request.matchdict.get('process_id')
        value = request.matchdict.get('value')
        data = {"success": True}
        data["items"] = PROCESSES[process_id][value]
    except:
        data = {"success": False}
    return data