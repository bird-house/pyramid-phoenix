$(function() {
  // Activate user
  $(".activate").button({
    text: false,
  }).click(function( event ) {
    var email = $(this).attr('data-value');
    $.getJSON(
      '/settings/users/'+email+'/activate.json',
      {},
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
      '/settings/users/'+email+'/edit.json',
      {},
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
