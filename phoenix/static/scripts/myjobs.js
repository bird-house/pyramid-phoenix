$(function() {

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
	var numRows = $("table tr").length - 1;
	if (numRows < json.length) {
	  location.reload();
	}
	else {
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
	}
	
        if (finished == true) {
          clearInterval(timerId);
        }
      }
    );
  };

  // refresh job list each 3 secs ...
  timerId = setInterval(function() {
    updateJobs();
  }, 3000); 

});
