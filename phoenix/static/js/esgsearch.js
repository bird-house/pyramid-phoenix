var init_esgsearch = function(oid) {
  jQuery(".tm-selection").tagsManager({
    prefilled: ["variable:hus", "experiment:decadal1960"],
    preventSubmitOnEnter: true,
    delimiters: [9, 13, 44],
    maxTags: 2,
    tagClass: 'tm-tag tm-tag-success',
    hiddenTagListId: oid,
  });

  jQuery(".tm-facets").tagsManager({
    //prefilled: ["hello"],
    preventSubmitOnEnter: true,
    delimiters: [9, 13, 44],
    //maxTags: 1,
    tagClass: 'tm-tag tm-tag-info',
    tagCloseIcon: '+',
  });

  jQuery(".tm-facet").tagsManager({
    //prefilled: ["MPI-M", "NCC", "MIROC", "BCC"],
    preventSubmitOnEnter: true,
    delimiters: [9, 13, 44],
    //maxTags: 4,
    tagClass: 'tm-tag tm-tag-warning tm-tag-mini',
    tagCloseIcon: '+',
  });
};


(function($) {

  "use strict";

  var url = 'http://adelie.d.dkrz.de:8090/esg-search/search';
  var limit = '0';
  var distrib = 'false';
  var format = 'application%2Fsolr%2Bjson';
    
  $.esgsearch = function(constraints) {
    var constraint_param = '';
    if (constraints != null) {
      var searchConstraints = constraints.split(",");
      $.each(searchConstraints, function(i, constraint) {
	var facet_constraint = constraint.split(":");
	constraint_param += '&' + facet_constraint[0] + '=' + facet_constraint[1];
      });
    };

    var searchURL = url + '?' + 'facets=*' + constraint_param + '&limit=' + limit + '&distrib=' + distrib + '&format=' + format;
   
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


