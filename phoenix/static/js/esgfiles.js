(function($) {  
  $.extend({
    EsgFileSearch: function(options) {
      var defaults = {
        oid: null,
        url: null,
        distrib: 'true',
        latest: 'true',
        replica: 'false',
        query: '*',
        constraints: 'project:CMIP5,product:output1',
        limit: 1,
        type: 'File',
      };
      var searchOptions = $.extend(defaults, options);

      var init = function() {
        execute();
      };

      var execute = function() {
        var format = 'application%2Fsolr%2Bjson';
        var servlet = 'search';
       

        var searchURL = searchOptions.url + '/' + servlet + '?';
        searchURL += 'type=' + searchOptions.type;
        searchURL += '&facets=*';
        var tags = searchOptions.constraints.split(",");
        var constraints = '';
        $.each(tags, function(i, tag) {
          var constraint = tag.split(":");
          constraints += '&' + constraint[0] + '=' + constraint[1];
        });
        searchURL += constraints;
        searchURL += '&limit=' + searchOptions.limit;
        searchURL += '&distrib=' + searchOptions.distrib;
        if (searchOptions.latest == 'true') {
          searchURL += '&latest=true';
        }
        if (searchOptions.replica == 'false') {
          searchURL += '&replica=false';
        }
        searchURL += '&format=' + format;
        searchURL += '&query=' +  searchOptions.query;

        console.log(searchURL);
        $.getJSON(searchURL, function(json) {
          var facet_counts = json.facet_counts.facet_fields;
          var facets = [];
          $.each(facet_counts, function(tag, values) {
            if (values.length > 2) {
              facets.push(tag);
            }
          });
        });
      };

      init();
    },
  });
})(jQuery);