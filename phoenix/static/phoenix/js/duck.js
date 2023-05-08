$(function() {
    var search_value = "";
    var search = function(value) {
      $.getJSON("/search/crai/"+value, function(data) {
        $.each( data.items, function( i, item ) {
          update_field(item.name, item.value, item.title);
        });
      });
    };

    var update_field = function(name, value, title) {
      console.log("update_field", name);
      var field = $("[name='"+name+"']");
      field.val(value);
      field.attr("title", title)
    };

    var init = function() {
      console.log("init");
      $.getJSON("/search/crai/default", function(data) {
        $.each( data.items, function( i, item ) {
          var active_field = $("[name='"+item.name+"']");
          //search_value = item.title;
          active_field.change(function() {
            var value = active_field.val();
            if (value != search_value) {
              search_value = value;
              search(value);
            };
          });
        });
      });
    }

    init();
  });