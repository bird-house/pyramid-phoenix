$(function() {
  // Delete catalog entry
  $("a.catalog-delete").click(function(e) {
    e.preventDefault();
    var wps_url = $(this).closest('ul').attr('id');
    var entry = $(this).closest('tr');
    $.getJSON(
      '/delete.entry',
      {'id': wps_url},
      function(json) {
        entry.remove();
      }
    );
  });
  
});