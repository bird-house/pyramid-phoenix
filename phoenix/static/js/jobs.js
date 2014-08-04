$(function() {

  // update job table with current values
  var update_jobs = function() {
     $.getJSON(
      '/update.jobs',
      {},
      function(json) {
        $.each(json, function(index, job) {

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
          }

          $("#status-"+job.job_id).attr('class', status_class);
          $("#status-"+job.job_id).text(job.status);
          $("#message-"+job.job_id).text(job.message);
          $("#progress-"+job.job_id).attr('style', "width: "+job.progress+"%");
          $("#progress-"+job.job_id).text(job.progress);
        });
      }
    );
  };

  // refresh job list each sec ...
  var i = setInterval(function() {
    update_jobs();
  }, 1000); 

  // Refresh job list ...
  $("a.job-refresh").click(function(e) {
    e.preventDefault();
    update_jobs();
  });

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
    var job_id = $(this).attr('data-value');
    var row = $(this).closest('tr');
    $.getJSON(
      '/delete.job',
      {'job_id': job_id},
      function(json) {
        row.remove();
      }
    );
  });
 
  // show details
  $(".show").button({
    text: false,
  }).click(function( event ) {
    var job_id = $(this).attr('data-value');
    window.location.href = "/output_details?job_id=" + job_id;
  });
 
});
