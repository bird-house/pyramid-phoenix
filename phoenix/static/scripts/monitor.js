$(function() {

  // monitor
  // ------
  
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
