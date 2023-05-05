$(function() {

    $("#deformField2").change(function() {
      var dataset_name = $("#deformField2").val();
      //console.log(dataset_name);
      $.getJSON("/search/crai/"+dataset_name, function(data) {
        console.log(data.result);
        dataset_name_tooltip = data.result.dataset_name_tooltip;
        file = data.result.file;
        file_tooltip = data.result.file_tooltip;
        variable_name = data.result.variable_name;
        variable_name_tooltip = data.result.variable_name_tooltip;

        $("#item-deformField2").attr("title", dataset_name_tooltip);
        $("#deformField3").val(file);
        $("#deformField3").attr("title", file_tooltip);
        $("#item-deformField3").attr("title", file_tooltip);
        $("#deformField4").val(variable_name);
        $("#item-deformField4").attr("title", variable_name_tooltip);
      });
    });

    $("#deformField2").val("HadCRUT5");
    $("#item-deformField2").attr("title", "");
    $("#deformField3").val("https://www.metoffice.gov.uk/hadobs/hadcrut5/data/current/non-infilled/HadCRUT.5.0.1.0.anomalies.ensemble_mean.nc");
    $("#deformField3").attr("title", "Enter a URL to your HadCRUT5 netcdf file.");
    $("#item-deformField3").attr("title", "Enter a URL to your HadCRUT5 netcdf file.");
    $("#deformField4").val("tas_mean");
    $("#item-deformField4").attr("title", "tas_mean");
  });