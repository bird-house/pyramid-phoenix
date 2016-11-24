$(function() {

  var timerId = 0;

  // refresh job list each 1 secs ...
  timerId = setInterval(function() {
    location.reload();
    console.log("running");
  }, 1000);

});
