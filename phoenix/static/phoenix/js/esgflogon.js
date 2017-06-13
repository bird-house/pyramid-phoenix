$(function() {

  var timerId = 0;

  var checkLogon = function() {
    $.getJSON(
      '/esgf/check_logon.json',
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
    checkLogon();
  }, 1000);

});
