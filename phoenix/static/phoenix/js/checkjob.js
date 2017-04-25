$(function() {

  var timerId = 0;

  var checkQueue = function() {
    $.getJSON(
      '/processes/check_job.json',
      {},
      function(json) {
        if (json.status == 'ready') {
          clearInterval(timerId);
          location.reload();
        }
      }
    );
  };

  // refresh job list each 1 secs ...
  timerId = setInterval(function() {
    checkQueue();
  }, 1000);

});
