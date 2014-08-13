$(function() {

  // open reference in new window
  $("a.reference").click(function( event ) {
    $(this).attr('target', '_blank');
  });
  
  // Open publish form when publish is clicked
  $(".publish").button({
    text: false,
  }).click(function( event ) {
    var outputid = $(this).attr('data-value');
    $.getJSON(
      '/publish.output',
      {'outputid': outputid},
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
