$(function() {
    var service_id = "";
    var process_id = "";
    var search_value = "";
    var search = function(value) {
      console.log(service_id, process_id, value);
      $.getJSON("/search/"+service_id+"/"+process_id+"/"+value, function(data) {
        $.each( data.items, function( i, item ) {
          update_field(item.name, item.value, item.title);
        });
      });
    };

    var update_field = function(name, value, title) {
      //console.log("update_field", name);
      var field = $("[name='"+name+"']");
      field.val(value);
      field.attr("title", title)
    };

    var init = function() {
      //console.log("init");
      // const url = $(location).attr('href');
      const url = window.location.search;
      const urlParams = new URLSearchParams(url);
      service_id = urlParams.get('wps');
      process_id = urlParams.get('process');
      console.log(Array.from(urlParams.keys()));
      $.getJSON("/search/"+service_id+"/"+process_id+"/default", function(data) {
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
    search("HadCRUT5");
  });