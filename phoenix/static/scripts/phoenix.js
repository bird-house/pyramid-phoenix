$(function() {

  // enabled tooltip
  $('[data-toggle="tooltip"]').tooltip()
  
  // MyJobs
  // ------
  
  var timerId = 0;

  // update job table with current values
  var updateJobs = function() {
     $.getJSON(
      '/myjobs/update.json',
      {},
      function(json) {
        //var finished = true;
	var finished = false;
        $.each(json, function(index, job) {
            var status_class = ''
            if (job.status == 'ProcessSucceeded') {
              status_class = 'glyphicon glyphicon-ok-sign text-success';
            }
            else if (job.status == 'ProcessFailed') {
              status_class = 'glyphicon glyphicon-remove-sign text-danger';
            }
            else if (job.status == 'ProcessPaused') {
              status_class = 'glyphicon glyphicon-paused text-muted';
            }
            else if (job.status == 'ProcessStarted' || job.status == 'ProcessAccepted') {
              status_class = 'glyphicon glyphicon-cog text-muted';
              //finished = false;
            }
            else {
              status_class = 'glyphicon glyphicon-question-sign text-danger';
            }

            $("#status-"+job.identifier).attr('class', status_class);
            $("#status-"+job.identifier).attr('title', job.status);
            $("#duration-"+job.identifier).text(job.duration);
            $("#progress-"+job.identifier).attr('style', "width: "+job.progress+"%");
            $("#progress-"+job.identifier).text(job.progress + "%");
        });

        if (finished == true) {
          clearInterval(timerId);
        }
      }
    );
  };

  // refresh job list each 5 secs ...
  timerId = setInterval(function() {
    updateJobs();
  }, 5000); 

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
