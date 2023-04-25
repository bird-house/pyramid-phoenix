$(function() {

    //console.log("hello");
  
    $("#deformField2").change(function() {
      dataset_name = $("#deformField2").val();
      //console.log(dataset_name);

      if (dataset_name == "HadCRUT4") {
        dataset_name_tooltip = "HadCRUT4"
        file = "https://www.metoffice.gov.uk/hadobs/hadcrut4/data/current/gridded_fields/HadCRUT.4.6.0.0.median_netcdf.zip";
        file_tooltip = "Enter a URL to your HadCRUT4 netcdf file."
        variable_name = "temperature_anomaly";
        variable_name_tooltip = "temperature_anomaly";
      } else {
        dataset_name_tooltip = "HadCRUT5"
        file = "https://www.metoffice.gov.uk/hadobs/hadcrut5/data/current/non-infilled/HadCRUT.5.0.1.0.anomalies.ensemble_mean.nc";
        file_tooltip = "Enter a URL to your HadCRUT5 netcdf file."
        variable_name = "tas_mean";
        variable_name_tooltip = "tas_mean";
      }

      $("#item-deformField2").attr("title", dataset_name_tooltip);
      $("#deformField3").val(file);
      $("#deformField3").attr("title", file_tooltip);
      $("#item-deformField3").attr("title", file_tooltip);
      $("#deformField4").val(variable_name);
      $("#item-deformField4").attr("title", variable_name_tooltip);
    });

    $("#deformField2").val("HadCRUT5");
    $("#item-deformField2").attr("title", "HadCRUT5");
    $("#deformField3").val("https://www.metoffice.gov.uk/hadobs/hadcrut5/data/current/non-infilled/HadCRUT.5.0.1.0.anomalies.ensemble_mean.nc");
    $("#deformField3").attr("title", "Enter a URL to your HadCRUT5 netcdf file.");
    $("#item-deformField3").attr("title", "Enter a URL to your HadCRUT5 netcdf file.");
    $("#deformField4").val("tas_mean");
    $("#item-deformField4").attr("title", "tas_mean");
  });