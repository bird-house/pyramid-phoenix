$(function() {
  // Refresh job list ...
  $("a.job-refresh").click(function(e) {
    e.preventDefault();
    location.reload()
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
 
  // refresh page each 5 secs
  var i = setInterval(function() {
    $.getJSON(
      'update.job', 
      {'job_id': 0},
      function(json) {
        if (json == null) {
          clearInterval(i);
          location.reload(true);
          return;
        }

        location.reload(true);
      })
  }, 5000);

});
