$(function() {
  // Delete catalog entry
  $("a.catalog-delete").click(function(e) {
    e.preventDefault();
    var wps_url = $(this).closest('ul').attr('id');
    var entry = $(this).closest('tr');
    $.getJSON(
      '/delete.entry',
      {'url': wps_url},
      function(json) {
        entry.remove();
      }
    );
  });
  
  // Edit a task when the edit link is clicked in the actions dropdown
  $("a.catalog-edit").click(function(e) {
    e.preventDefault();
    var wps_url = $(this).closest('ul').attr('id');
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
