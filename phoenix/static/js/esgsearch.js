(function($) {  
  $.extend({
    EsgSearch: function(options) {
      var defaults = {
        url: null,
        query: '*',
        constraints: null,
        distrib: true,
        latest: true,
        replica: false,
        temporal: false,
        start: '',
        end: '',
        spatial: false,
        bbox: '',
        type: 'Dataset',
        callback: function(json) {callback(json)},
      };
      var searchOptions = $.extend(defaults, options);

      var init = function() {
        execute();
      };

      var callback = function(json) {
        console.log(json.facet_counts.facet_fields);
      };
      
      var execute = function() {
        var limit = '0';
        var format = 'application%2Fsolr%2Bjson';
        var constraints = ''; 
        var servlet = 'search';
        var tags = searchOptions.constraints.split(",");
        $.each(tags, function(i, tag) {
          var constraint = tag.split(":");
          constraints += '&' + constraint[0] + '=' + constraint[1];
        });

        var searchURL = searchOptions.url + '/' + servlet + '?';
        searchURL += 'type=' + searchOptions.type;
        searchURL += '&facets=*';
        searchURL += constraints; 
        searchURL += '&limit=' + limit;
        if (searchOptions.distrib == true) {
          searchURL += '&distrib=true';
        } else {
          searchURL += '&distrib=false';
        }
        if (searchOptions.latest == true) {
          searchURL += '&latest=true';
        }
        if (searchOptions.replica == false) {
          searchURL += '&replica=false';
        }
        searchURL += '&format=' + format;
        searchURL += '&query=' +  searchOptions.query;
        if (searchOptions.temporal == true) {
          searchURL += '&start=' +  searchOptions.start;
          searchURL += '&end=' +  searchOptions.end;
        }
        if (searchOptions.spatial == true) {
          searchURL += '&bbox=' +  searchOptions.bbox;
        }

        console.log(searchURL);
        $.getJSON(searchURL, function(json) {
          searchOptions.callback(json);
        });
      };

      init();
    },
  });
})(jQuery);



