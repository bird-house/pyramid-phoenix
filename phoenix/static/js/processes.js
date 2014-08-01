$(function() {
  // execute process
  $("a.process-execute").click(function(e) {
    e.preventDefault();
    var identifier = $(this).closest('ul').attr('id');
    window.location.href = "/execute?identifier=" + identifier;
  });

  $("#execute").button({
    text: false,
  }).click(function( event ) {
    var identifier = $(this).attr('data-value');
    window.location.href = "/execute?identifier=" + identifier;
  });

  $("#info").button({
    text: false,
  }).click(function( event ) {
    alert('not available yet!');
  });

});
