$(function() {
 
  $(".execute").button({
    text: false,
  }).click(function( event ) {
    var identifier = $(this).attr('data-value');
    window.location.href = "/execute?identifier=" + identifier;
  });

  $(".info").button({
    text: false,
  }).click(function( event ) {
    alert('not available yet!');
  });

});
