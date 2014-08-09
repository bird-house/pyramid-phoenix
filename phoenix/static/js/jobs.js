$(function() {

  var timerId = 0;

  // update job table with current values
  var updateJobs = function() {
     $.getJSON(
      '/update.jobs',
      {},
      function(json) {
        var finished = true;
        $.each(json, function(index, job) {
          // update only if necessary
          var currentStatus = $("#status-"+job.identifier).text();
          if (! (currentStatus in ['ProcessSucceeded', 'ProcessFailed', 'Exception']) ) {
            var status_class = 'label'
            if (job.status == 'ProcessSucceeded') {
              status_class += ' label-success';
            }
            else if (job.status == 'ProcessFailed') {
              status_class += ' label-warning';
            }
            else if (job.status == 'Exception') {
              status_class += ' label-important';
            }
            else {
              status_class += ' label-info';
              finished = false;
            }

            $("#status-"+job.identifier).attr('class', status_class);
            $("#status-"+job.identifier).text(job.status);
            $("#message-"+job.identifier).text(job.message);
            $("#progress-"+job.identifier).attr('style', "width: "+job.progress+"%");
            $("#progress-"+job.identifier).text(job.progress);
          }
        });

        if (finished == true) {
          clearInterval(timerId);
        }
      }
    );
  };

  // refresh job list each sec ...
  timerId = setInterval(function() {
    updateJobs();
  }, 1000); 

  // Delete all jobs
  $("a.job-delete-all").click(function(e) {
    e.preventDefault();
    $.getJSON(
      '/deleteall.job',
      {},
      function(json) {
        location.reload()
      }
    );
  });

  // delete job
  $(".delete").button({
    text: false,
  }).click(function( event ) {
    var jobid = $(this).attr('data-value');
    var row = $(this).closest('tr');
    $.getJSON(
      '/delete.job',
      {'jobid': jobid},
      function(json) {
        row.remove();
      }
    );
  });
 
  // show details
  $(".show").button({
    text: false,
  }).click(function( event ) {
    var jobid = $(this).attr('data-value');
    // TODO: fix the call
    window.location.href = "/output_details?jobid=" + jobid;
  });
 
});
