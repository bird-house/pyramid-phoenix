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

  $.esgsearch = function() {
    var url = 'http://adelie.d.dkrz.de:8090/esg-search/search?limit=0&distrib=false&facets=*&format=application%2Fsolr%2Bjson'
    $.getJSON(url, function(json) {
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
  }

})(jQuery);


