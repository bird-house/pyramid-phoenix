$(function() {

    var search_value = "HadCRUT5";
    var search = function(value) {
      $.getJSON("/search/crai/"+value, function(data) {
        console.log(data.result);
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

    var active_field = $("[name='dataset_name']");
    active_field.change(function() {
      var value = active_field.val();
      if (value != search_value) {
        //console.log(value);
        search_value = value;
        search(value);
      };
    });

    search(search_value);
  });