$(function() {


  // Add url to cart
  // ----------------------------------------------
  
  $('.add-to-cart').on('click', function (event) {
    var url = $(this).attr('data-value');
    var btn = $(this);
    // call json 
    $.getJSON(
      '/add_to_cart.json', {'url': url}, function(json) {
        if (json) {
          btn.attr('class', "btn btn-default btn-xs pull-right remove-from-cart");
          btn.attr('title', "Remove from Cart");
          $("> icon", btn).attr('class', 'fa fa-lg fa-times');
        }
      }
    );
  })

  // Remove url from cart
  // ----------------------------------------------
  
  $('.remove-from-cart').on('click', function (event) {
    var url = $(this).attr('data-value');
    var btn = $(this);
    // call json 
    $.getJSON(
      '/remove_from_cart.json', {'url': url}, function(json) {
        if (json) {
          btn.attr('class', "btn btn-default btn-xs pull-right add-to-cart");
          btn.attr('title', "Add to Cart");
          $("> icon", btn).attr('class', 'fa fa-lg fa-cart-plus');
        }
      }
    );
  })
  
});
