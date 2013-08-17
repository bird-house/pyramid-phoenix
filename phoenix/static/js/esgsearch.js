var selected_facet_handler = function (facet) {
  alert('facet = ' + facet);
};

var selected_facet_value_handler = function (facet_value) {
  alert('facet_value = ' + facet_value);
};

var init_esgsearch = function(oid) {
  jQuery(".tm-selection").tagsManager({
    prefilled: ["experiment:decadal1960"],
    preventSubmitOnEnter: true,
    delimiters: [9, 13, 44],
    //maxTags: 2,
    tagClass: 'tm-tag tm-tag-success',
    hiddenTagListId: oid,
  });

  jQuery(".tm-facets").tagsManager({
    //prefilled: ["hello"],
    preventSubmitOnEnter: true,
    delimiters: [9, 13, 44],
    //maxTags: 1,
    tagClass: 'tm-tag tm-tag-info',
    isSelectable: true,
    selectHandler: selected_facet_handler,
  });

  jQuery(".tm-facet").tagsManager({
    //prefilled: ["MPI-M", "NCC", "MIROC", "BCC"],
    preventSubmitOnEnter: true,
    delimiters: [9, 13, 44],
    //maxTags: 4,
    tagClass: 'tm-tag tm-tag-warning tm-tag-mini',
    isSelectable: true,
    selectHandler: selected_facet_value_handler,
  });
};


(function($) {

  "use strict";

  var url = 'http://tracy.local:8090/esg-search/search';
  var limit = '0';
  var distrib = 'false';
  var format = 'application%2Fsolr%2Bjson';
    
  $.esgsearch = function() {
    var constraints = '';
    var tags = $("#deformField1").val().split(",");
    $.each(tags, function(i, tag) {
      var constraint = tag.split(":");
      constraints += '&' + constraint[0] + '=' + constraint[1];
    });

    var searchURL = url + '?' + 'facets=*' + constraints + '&limit=' + limit + '&distrib=' + distrib + '&format=' + format;
   
    $.getJSON(searchURL, function(json) {
      var tags = json.responseHeader.params['facet.field'];
      $.each(tags, function(i, tag) {
	jQuery(".tm-facets").tagsManager('pushTag', tag);
      });
      var counts = json.facet_counts.facet_fields['institute'];
      $.each(counts, function(i,value) {
	if (i % 2 == 0) {
	  jQuery(".tm-facet").tagsManager('pushTag', value);
	}
      });
      
    });
  };

})(jQuery);


