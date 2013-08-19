(function($) {
  $.extend({
    EsgSearch: function(options) {
      var defaults = {
	oid: null,
	url: 'http://adelie.d.dkrz.de:8090/esg-search/search',
	limit: '0',
	distrib: 'false',
	format: 'application%2Fsolr%2Bjson',
      };
      var searchOptions = $.extend(defaults, options);
      var selectedFacet = 'institute';

      var init = function() {
	init_constraints(searchOptions.oid);
	init_facets();
	init_facet_values();
	execute();
      };

      var deleted_constraint_handler = function(constraint) {
	execute();
      };

      var selected_facet_handler = function (facet) {
	selectedFacet = facet;
	$('#search-label-category').text("Category: " + selectedFacet)
	execute();
      };

      var selected_facet_value_handler = function (facet_value) {
	value = selectedFacet  + ':' + facet_value;
	$(".tm-selection").tagsManager('pushTag', value);
	execute();
      };

      var update_counts = function(counts) {
	$('#search-label-counts').text("Datasets: " + counts)
      };

      var init_constraints = function(oid) {
	$(".tm-selection").tagsManager({
	  //prefilled: ["experiment:decadal1960"],
	  preventSubmitOnEnter: true,
	  delimiters: [9, 13, 44],
	  //maxTags: 2,
	  tagClass: 'tm-tag tm-tag-success',
	  hiddenTagListId: oid,
	  deleteHandler: deleted_constraint_handler,
	});
      };

      var init_facets = function() {
	$(".tm-facets").tagsManager({
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
	$(".tm-facet").tagsManager({
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
	var tags = $("#" + searchOptions.oid).val().split(",");
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
	  var facet_counts = json.facet_counts.facet_fields;
	  var facets = [];
	  $.each(facet_counts, function(tag, values) {
	    if (values.length > 2) {
	      facets.push(tag);
	    }
	  });
	  $(".tm-facets").tagsManager('empty');
	  $.each(facets.sort(), function(i, tag) {
	    jQuery(".tm-facets").tagsManager('pushTag', tag);
	  });
	  var counts = json.facet_counts.facet_fields[selectedFacet];
	  $(".tm-facet").tagsManager('empty');
	  var facet_values = [];
	  $.each(counts, function(i,value) {
	    if (i % 2 == 0) {
	      facet_values.push(value);
	    }
	  });
	  $.each(facet_values.sort(), function(i,value) {
	    jQuery(".tm-facet").tagsManager('pushTag', value);
	  });
	  update_counts(json.response.numFound);
	});
      };

      init();
    },
  });
})(jQuery);



