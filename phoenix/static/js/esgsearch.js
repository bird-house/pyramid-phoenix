(function($) {  
  $.extend({
    EsgSearch: function(options) {
      var defaults = {
        url: null,
        query: '*', // TODO: rename query to freetext
        datasetId: null,
        constraints: null,
        limit: 0,
        facets: '*',
        distrib: true,
        latest: true,
        replica: false,
        temporal: false,
        start: '',
        end: '',
        spatial: false,
        bbox: '',
        type: 'Dataset',
        callback: function(json) { console.log('no callback defined.')},
      };
      var searchOptions = $.extend(defaults, options);

      var execute = function() {
        search(buildQuery());
      };

      var search = function(query) {
        var format = 'application%2Fsolr%2Bjson';
        var servlet = 'search';
        var searchURL = searchOptions.url + '/' + servlet + '?';
        searchURL += query;
        searchURL += '&format=' + format;

        $.getJSON(searchURL, function(json) {
          searchOptions.callback(json);
        });
      };

      var buildQuery = function() {
        var query = '';

        query += 'type=' + searchOptions.type;
        query += '&facets=' + searchOptions.facets;
        query += '&limit=' + searchOptions.limit;

        if (searchOptions.datasetId != null) {
          query += '&dataset_id=' + searchOptions.datasetId;
        }
        
        var tags = searchOptions.constraints.split(",");
        $.each(tags, function(i, tag) {
          var constraint = tag.split(":");
          if (searchOptions.type != 'Aggregation' || constraint[0] == 'variable') {
            query += '&' + constraint[0] + '=' + constraint[1];
          }
        });
        
        if (searchOptions.distrib == true) {
          query += '&distrib=true';
        } else {
          query += '&distrib=false';
        }
        if (searchOptions.latest == true) {
          query += '&latest=true';
        }
        if (searchOptions.replica == false) {
          query += '&replica=false';
        }
        query += '&query=' + searchOptions.query;
        if (searchOptions.temporal == true) {
          query += '&start=' + searchOptions.start;
          query += '&end=' + searchOptions.end;
        }
        if (searchOptions.spatial == true) {
          query += '&bbox=' + searchOptions.bbox;
        }

        console.log(query);
        return query;
      };

      execute();
    },
  });
})(jQuery);



