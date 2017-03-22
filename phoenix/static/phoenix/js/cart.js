$(function() {


  // Add url to cart
  // ----------------------------------------------

  $(document.body).on('click', '.btn-cart-add' ,function() {
    var url = $(this).attr('data-value');
    var btn = $(this);
    // call json
    $.getJSON(
      '/add_to_cart.json', {'url': url}, function(json) {
        btn.removeClass('btn-cart-add');
        btn.addClass('btn-cart-remove');
        btn.attr('title', "Remove from Cart");
        $("> icon", btn).attr('class', 'fa fa-lg fa-times');
      }
    );
  })

  // Remove url from cart
  // ----------------------------------------------

  $(document.body).on('click', '.btn-cart-remove' ,function() {
    var url = $(this).attr('data-value');
    var btn = $(this);
    // call json
    $.getJSON(
      '/remove_from_cart.json', {'url': url}, function(json) {
        btn.removeClass('btn-cart-remove');
        btn.addClass('btn-cart-add');
        btn.attr('title', "Add to Cart");
        $("> icon", btn).attr('class', 'fa fa-lg fa-cart-plus');
      }
    );
  })

});
