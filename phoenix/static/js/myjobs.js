$(function() {

  var timerId = 0;

  // update job table with current values
  var updateJobs = function() {
     $.getJSON(
      '/myjobs/update.json',
      {},
      function(json) {
        var finished = true;
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
              finished = false;
            }

            $("#status-"+job.identifier).attr('class', status_class);
            $("#status-"+job.identifier).text(job.status);
            $("#message-"+job.identifier).text(job.status_message);
            $("#progress-"+job.identifier).attr('style', "width: "+job.progress+"%");
            $("#progress-"+job.identifier).text(job.progress);
        });

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
