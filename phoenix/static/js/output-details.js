$(function() {
  
  // Open publish form when the publish link is clicked
  $("a.output-publish").click(function(e) {
    e.preventDefault();
    var identifier = $(this).closest('ul').attr('id');
    $.getJSON(
      '/publish.output',
      {'identifier': identifier},
      function(json) {
        if (json) {
          form = $('#publish-form');
          
          // Set the title to Edit
          form.find('h3').text('Publish to Catalog Service');
          $.each(json, function(k, v) {
            // Set the value for each field from the returned json
            form.find('input[name="' + k + '"]').attr('value', v);
          });
          
          form.modal('show');
        }
      }
    );
  });

});
