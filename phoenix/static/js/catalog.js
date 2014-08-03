$(function() {
  // delete catalog entry
  $(".delete").button({
    text: false,
  }).click(function( event ) {
    var wps_url = $(this).attr('data-value');
    var row = $(this).closest('tr');
     $.getJSON(
      '/delete.entry',
      {'url': wps_url},
      function(json) {
        row.remove();
      }
    );
  });
  
  // edit catalog entry
  $(".edit").button({
    text: false,
  }).click(function( event ) {
    var wps_url = $(this).attr('data-value');
    $.getJSON(
      '/edit.entry',
      {'url': wps_url},
      function(json) {
        if (json) {
          catalog_form = $('#catalog-form');
          
          // Set the title to Edit
          catalog_form.find('h3').text('Edit WPS');
          $.each(json, function(k, v) {
            // Set the value for each field from the returned json
            catalog_form.find('input[name="' + k + '"]').attr('value', v);
          });
          
          catalog_form.modal('show');
        }
      }
    );
  });

});
