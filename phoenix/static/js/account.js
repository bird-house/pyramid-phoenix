$(function() {
  // update user token
  $("a.user-update-token").click(function(e) {
    e.preventDefault();
    $.getJSON(
      '/update.token',
      {},
      function(json) {
        console.log('user token updated')
        location.reload()
      }
    );
  });

});