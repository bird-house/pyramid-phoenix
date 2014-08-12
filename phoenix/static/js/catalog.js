$(function() {
  // delete catalog entry
  $(".delete").button({
    text: false,
  }).click(function( event ) {
    var identifier = $(this).attr('data-value');
    var row = $(this).closest('tr');
     $.getJSON(
      '/catalog.delete',
      {'identifier': identifier},
      function(json) {
        //row.remove();
        console.log("delete catalog entry not implemented yet");
        location.reload()
      }
    );
  });

  // edit catalog entry
  $(".edit").button({
    text: false,
  }).click(function( event ) {
    var identifier = $(this).attr('data-value');
    var row = $(this).closest('tr');
     $.getJSON(
      '/catalog.edit',
      {'identifier': identifier},
      function(json) {
        //row.remove();
        console.log("edit catalog entry not implemented yet");
        location.reload()
      }
    );
  });
  
});
