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