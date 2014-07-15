$(function() {
  // Delete user entry
  $("a.user-delete").click(function(e) {
    e.preventDefault();
    var wps_url = $(this).closest('ul').attr('id');
    var entry = $(this).closest('tr');
    $.getJSON(
      '/delete.user',
      {'url': wps_url},
      function(json) {
        entry.remove();
      }
    );
  });
  
  // Edit a user when the edit link is clicked in the actions dropdown
  $("a.user-edit").click(function(e) {
    e.preventDefault();
    var user_id = $(this).closest('ul').attr('id');
    $.getJSON(
      '/edit.user',
      {'user_id': user_id},
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
