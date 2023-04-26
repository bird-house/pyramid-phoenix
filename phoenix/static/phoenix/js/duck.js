$(function() {

    //console.log("hello");
    const description_hadcrut4 = "" + 
      "HadCRUT4 Training dataset: 82133 samples of near surface temperature anomalies" +
      " from the 20th century reanalysis dataset (https://psl.noaa.gov/data/20thC_Rean/)" +
      " spanning the period 1870-2009." +
      " \nMask dataset: masks of missing values extracted from the HadCRUT4 dataset for the period 1850-2014.";
    const description_hadcrut5 = "" +
      "HadCRUT5 Training dataset: 82133 samples of near surface temperature anomalies" +
      " from the 20th century reanalysis dataset (https://psl.noaa.gov/data/20thC_Rean/)" +
      " spanning the period 1870-2009." +
      " \nMask dataset: masks of missing values extracted from the HadCRUT5 dataset for the period 1850-2014.";
  
    $("#deformField2").change(function() {
      var dataset_name = $("#deformField2").val();
      //console.log(dataset_name);

      if (dataset_name == "HadCRUT4") {
        dataset_name_tooltip = description_hadcrut4;
        file = "https://www.metoffice.gov.uk/hadobs/hadcrut4/data/current/gridded_fields/HadCRUT.4.6.0.0.median_netcdf.zip";
        file_tooltip = "Enter a URL to your HadCRUT4 netcdf file.";
        variable_name = "temperature_anomaly";
        variable_name_tooltip = "temperature_anomaly";
      } else {
        dataset_name_tooltip = description_hadcrut5;
        file = "https://www.metoffice.gov.uk/hadobs/hadcrut5/data/current/non-infilled/HadCRUT.5.0.1.0.anomalies.ensemble_mean.nc";
        file_tooltip = "Enter a URL to your HadCRUT5 netcdf file.";
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
    $("#item-deformField2").attr("title", description_hadcrut5);
    $("#deformField3").val("https://www.metoffice.gov.uk/hadobs/hadcrut5/data/current/non-infilled/HadCRUT.5.0.1.0.anomalies.ensemble_mean.nc");
    $("#deformField3").attr("title", "Enter a URL to your HadCRUT5 netcdf file.");
    $("#item-deformField3").attr("title", "Enter a URL to your HadCRUT5 netcdf file.");
    $("#deformField4").val("tas_mean");
    $("#item-deformField4").attr("title", "tas_mean");
  });