
/*
$("#openid").submit( function(event) {
  console.log($('#username').val());
  var username = $('#username').val();
  var id = $('#id').val();
  $('#id').val(id+'/'+username);
  console.log($('#id').val()); 
  event.preventDefault();
});
*/

$(document).ready(function (e) {
  authomatic.setup({
    backend: '/login/',
    // Called when the popup gets open.
    onPopupOpen: function(url) {
      console.log('open popup')
    },
    // Called when the login procedure is over.
    onLoginComplete: function(result) {
      console.log('login complete')
    },
  });
        
  authomatic.popupInit();
});
