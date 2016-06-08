$(function() {

  // enabled tooltip
  $('[data-toggle="tooltip"]').tooltip()

  // toggle all checkbox
  $('[data-toggle="checkbox"]').change(function () {
    $('input[type=checkbox]').prop('checked', this.checked);
  });

  // Open job caption form when caption is clicked
  $(".caption").button({
    text: false,
  }).click(function( event ) {
    var job_id = $(this).attr('data-value');
    $.getJSON(
      '/edit_job.json',
      {'job_id': job_id},
      function(json) {
        if (json) {
          form = $('#caption-form');
          
          // Set the title
          form.find('h3').text('Edit Caption');
          $.each(json, function(k, v) {
            // Set the value for each field from the returned json
            form.find('input[name="' + k + '"]').attr('value', v);
          });
          
          form.modal('show');
        }
      }
    );
  });


  // Open job caption form when caption is clicked
  $(".labels").button({
    text: false,
  }).click(function( event ) {
    var job_id = $(this).attr('data-value');
    $.getJSON(
      '/edit_job.json',
      {'job_id': job_id},
      function(json) {
        if (json) {
          form = $('#labels-form');
          
          // Set the title
          form.find('h3').text('Edit Labels');
          $.each(json, function(k, v) {
            // Set the value for each field from the returned json
            form.find('input[name="' + k + '"]').attr('value', v);
          });
          
          form.modal('show');
        }
      }
    );
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
          
          // Set the title
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

  // Open upload form when upload is clicked
  $(".upload").button({
    text: false,
  }).click(function( event ) {
    var outputid = $(this).attr('data-value');
    $.getJSON(
      '/upload.output',
      {'outputid': outputid},
      function(json) {
        if (json) {
          form = $('#upload-form');
          
          // Set the title
          form.find('h3').text('Upload to Swift Cloud');
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
