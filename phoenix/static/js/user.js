$(function() {
  // delete user
  $(".delete").button({
    text:false,
  }).click(function( event ) {
    var email = $(this).attr('data-value');
    var row = $(this).closest('tr');
    $.getJSON(
      '/delete.user',
      {'email': email},
      function(json) {
        row.remove();
      }
    );
  });

  // Activate user
  $(".activate").button({
    text: false,
  }).click(function( event ) {
    var email = $(this).attr('data-value');
    $.getJSON(
      '/activate.user',
      {'email': email},
      function(json) {
        location.reload();
      }
    );
  });
  
  // edit user
  $(".edit").button({
    text: false,
  }).click(function( event ) {
    var email = $(this).attr('data-value');
    $.getJSON(
      '/edit.user',
      {'email': email},
      function(json) {
        if (json) {
          form = $('#user-form');
          
          // Set the title to Edit
          form.find('h3').text('Edit User');
          $.each(json, function(k, v) {
            // Set the value for each field from the returned json
            form.find('input[name="' + k + '"]').attr('value', v);
          });
          
          form.modal('show');
        }
      }
    );
  });

});
