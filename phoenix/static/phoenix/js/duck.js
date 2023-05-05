$(function() {

    var search = function(value) {
      $.getJSON("/search/crai/"+value, function(data) {
        //console.log(data.result);
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
    };

    $("#deformField2").change(function() {
      var dataset_name = $("#deformField2").val();
      //console.log(dataset_name);
      search(dataset_name);
      
    });

    search("HadCRUT5");
  });