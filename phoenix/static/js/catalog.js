$(function() {
  // delete catalog entry
  $(".delete").button({
    text: false,
  }).click(function( event ) {
    var identifier = $(this).attr('data-value');
    var row = $(this).closest('tr');
     $.getJSON(
      '/delete.entry',
      {'identifier': identifier},
      function(json) {
        //row.remove();
        console.log("delete entry from catalog not implemented yet");
        location.reload()
      }
    );
  });
  
});
