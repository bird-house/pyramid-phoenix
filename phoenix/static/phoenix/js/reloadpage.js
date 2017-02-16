$(function() {

  var timerId = 0;

  // refresh job list each 5 secs ...
  timerId = setInterval(function() {
    location.reload();
    console.log("running");
  }, 5000);

});
