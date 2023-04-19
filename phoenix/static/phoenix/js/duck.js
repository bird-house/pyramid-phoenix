$(function() {
  
    $("#deformField2").change(function() {
      dataset_name = $("#deformField2").val();
      // console.log(dataset_name);

      if (dataset_name == "HadCRUT4") {
        file = "https://www.metoffice.gov.uk/hadobs/hadcrut4/data/current/gridded_fields/HadCRUT.4.6.0.0.median_netcdf.zip";
        variable_name = "temperature_anomaly";
      } else {
        file = "https://www.metoffice.gov.uk/hadobs/hadcrut5/data/current/non-infilled/HadCRUT.5.0.1.0.anomalies.ensemble_mean.nc";
        variable_name = "tas_mean";
      }

      $("#deformField3").val(file);
      $("#deformField4").val(variable_name);
    });

  });