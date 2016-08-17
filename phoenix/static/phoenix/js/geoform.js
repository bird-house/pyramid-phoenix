$(function() {


  // Open cart form
  // ----------------------------------------------

  $(".btn-cart-select").button({
    text: false,
  }).click(function( event ) {
    console.log('cart button clicked');
    form = $('#cart-form');
    form.modal('show');
  });

});
