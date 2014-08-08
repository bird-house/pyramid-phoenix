$(function() {
 
  $(".execute").button({
    text: false,
  }).click(function( event ) {
    var identifier = $(this).attr('data-value');
    window.location.href = "/execute?identifier=" + identifier;
  });

});
