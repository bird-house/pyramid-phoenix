$(function() {


  // Open job caption form when caption is clicked
  // ----------------------------------------------

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
          //form.find('h4').text('Edit Caption');
          $.each(json, function(k, v) {
            // Set the value for each field from the returned json
            form.find('input[name="' + k + '"]').attr('value', v);
          });

          form.modal('show');
        }
      }
    );
  });

  // Open job labels form when labels is clicked
  // --------------------------------------------

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
          //form.find('h4').text('Edit labels');
          $.each(json, function(k, v) {
            // Set the value for each field from the returned json
            form.find('input[name="' + k + '"]').attr('value', v);
          });

          form.modal('show');
        }
      }
    );
  });

  // Select status
  // --------------

  var selectStatus = function() {
    default_location = '/monitor/';
    var location = $('#status-select option:selected').val();
    if (location){
      window.location = location;
    } else {
      window.location = default_location;
    }
  };

  $('#status-select').change( selectStatus );


  // Select limit
  // -------------

  var selectLimit = function() {
    default_location = '/monitor/';
    var location = $('#limit-select option:selected').val();
    if (location){
      window.location = location;
    } else {
      window.location = default_location;
    }
  };

  $('#limit-select').change( selectLimit );


  // monitor auto-update
  // -------------------
  
  var timerId = 0;

  // update job table with current values
  var updateJobs = function() {
    $.getJSON(
      '/active_jobs.json',
      {},
      function(json) {

        // count running jobs
        var numActiveJobs = $(".fa-gear").length;
        //console.log("active jobs in table = " + numActiveJobs + ", num jobs = " + json.length);
        if (numActiveJobs != json.length) {
          // TODO: this can also be done with jquery
          location.reload();
        }
        else {
          $.each(json, function(index, job) {
            var iconClass = ''
            if (job.status == 'ProcessStarted') {
              iconClass = "fa fa-gear fa-spin text-muted";
            }
            else if (job.status == 'ProcessSucceeded') {
              iconClass = "fa fa-check-circle text-success";
            }
            else if (job.status == 'ProcessFailed') {
              iconClass = "fa fa-times-circle text-danger";
            }
            else if (job.status == 'ProcessPaused') {
              iconClass = "fa fa-pause text-muted";
            }
            else {
              iconClass = "fa fa-fw fa-clock-o pulse text-muted";
            }
    
            $("#status-"+job.identifier).attr('class', iconClass);
            $("#status-"+job.identifier).attr('title', job.status);
            $("#progress-"+job.identifier).attr('style', "width: "+job.progress+"%");
            $("#progress-"+job.identifier).text(job.progress+"%");
            $("#duration-"+job.identifier).text(job.duration);
          });
        }
      }
    );
  };

  // refresh job list each 3 secs ...
  timerId = setInterval(function() {
    updateJobs();
  }, 3000); 
  

});
