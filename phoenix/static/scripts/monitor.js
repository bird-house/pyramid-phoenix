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

        if (json.length == 0) {
          clearInterval(timerId);
        }
        else {
          location.reload();
        }
      }
    );
  };

  // refresh job list each 5 secs ...
  timerId = setInterval(function() {
    updateJobs();
  }, 5000); 
  

});
