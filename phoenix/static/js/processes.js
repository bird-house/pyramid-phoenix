$(function() {
  // execute process
  $("a.process-execute").click(function(e) {
    e.preventDefault();
    var identifier = $(this).closest('ul').attr('id');
    window.location.href = "/execute?identifier=" + identifier;
  });

});
