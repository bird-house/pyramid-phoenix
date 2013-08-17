(function($) {
  $.extend({
    EsgSearch: function(options) {
      var defaults = {
	oid: null,
	url: 'http://tracy.local:8090/esg-search/search',
	limit: '0',
	distrib: 'false',
	format: 'application%2Fsolr%2Bjson',
      };
      var searchOptions = $.extend(defaults, options);

      var init = function() {
	init_constraints(searchOptions.oid);
	init_facets();
	init_facet_values();
	execute();
      };

      var selected_facet_handler = function (facet) {
	alert('facet = ' + facet);
      };

      var selected_facet_value_handler = function (facet_value) {
	alert('facet_value = ' + facet_value);
      };

      var init_constraints = function(oid) {
	jQuery(".tm-selection").tagsManager({
	  prefilled: ["experiment:decadal1960"],
	  preventSubmitOnEnter: true,
	  delimiters: [9, 13, 44],
	  //maxTags: 2,
	  tagClass: 'tm-tag tm-tag-success',
	  hiddenTagListId: oid,
	});
      };

      var init_facets = function() {
	jQuery(".tm-facets").tagsManager({
	  //prefilled: ["hello"],
	  preventSubmitOnEnter: true,
	  delimiters: [9, 13, 44],
	  //maxTags: 1,
	  tagClass: 'tm-tag tm-tag-info',
	  isSelectable: true,
	  selectHandler: selected_facet_handler,
	});
      };

      var init_facet_values = function() {
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
    
      var execute = function() {
	var constraints = '';
	var tags = $("#deformField1").val().split(",");
	$.each(tags, function(i, tag) {
	  var constraint = tag.split(":");
	  constraints += '&' + constraint[0] + '=' + constraint[1];
	});

	var searchURL = searchOptions.url + '?';
	searchURL += 'facets=*' + constraints; 
	searchURL += '&limit=' + searchOptions.limit; 
	searchURL += '&distrib=' + searchOptions.distrib; 
	searchURL += '&format=' + searchOptions.format;
   
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

      init();
    },
  });
})(jQuery);



