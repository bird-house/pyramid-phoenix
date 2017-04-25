$(function() {

  var timerId = 0;

  // refresh job list each 3 secs ...
  timerId = setInterval(function() {
    location.reload();
  }, 3000);

});
