(function($) {
  
  $.esgsearch = function() {
    var url = 'http://adelie.d.dkrz.de:8090/esg-search/search?limit=0&distrib=false&facets=*&format=application%2Fsolr%2Bjson'
    var tags = [];
    $.getJSON(url, function(json) {
      tags = json.responseHeader.params['facet.field'];
      $.each(tags, function(i, tag) {
	jQuery(".tm-facets").tagsManager('pushTag', tag);
      });
      counts = json.facet_counts.facet_fields['institute'];
      $.each(counts, function(i,value) {
	if (i % 2 == 0) {
	  jQuery(".tm-facet").tagsManager('pushTag', value);
	}
      });

    });
    return tags;
  }

})(jQuery);


