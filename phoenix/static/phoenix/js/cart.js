$(function() {


  // Add url to cart
  // ----------------------------------------------

  $(document.body).on('click', '.btn-cart-add' ,function() {
  //$('.btn-cart-add').on('click', function (event) {
    var url = $(this).attr('data-value');
    //var btn = $(this);
    // call json
    $.getJSON(
      '/add_to_cart.json', {'url': url}, function(json) {
        alert("add to cart");
        // TODO: this can also be done with jquery
        location.reload();
        // btn.attr('class', "btn btn-default btn-xs pull-right btn-cart-remove");
        // btn.attr('title', "Remove from Cart");
        // $("> icon", btn).attr('class', 'fa fa-lg fa-times');
      }
    );
  })

  // Remove url from cart
  // ----------------------------------------------
  $(document.body).on('click', '.btn-cart-remove' ,function() {
  //$('.btn-cart-remove').on('click', function (event) {
    var url = $(this).attr('data-value');
    //var btn = $(this)
    // call json
    $.getJSON(
      '/remove_from_cart.json', {'url': url}, function(json) {
        // TODO: this can also be done with jquery
        location.reload();
        // btn.attr('class', "btn btn-default btn-xs pull-right btn-cart-add");
        // btn.attr('title', "Add to Cart");
        // $("> icon", btn).attr('class', 'fa fa-lg fa-cart-plus');
      }
    );
  })

});
