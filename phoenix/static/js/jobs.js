$(function() {
  // Delete job
  $("a.job-delete").click(function(e) {
    e.preventDefault();
    var job_id = $(this).closest('ul').attr('id');
    var row = $(this).closest('tr');
    $.getJSON(
      '/delete.job',
      {'job_id': job_id},
      function(json) {
        row.remove();
      }
    );
  });

  // Show details
  $("a.job-show").click(function(e) {
    e.preventDefault();
    var job_id = $(this).closest('ul').attr('id');
    window.location.href = "/output_details?job_id=" + job_id;
  });

});
