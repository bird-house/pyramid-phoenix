(function($) {  
  $.extend({
    EsgSearch: function(options) {
      var defaults = {
        url: null,
        query: '*',
        datasetId: null,
        constraints: null,
        limit: 0,
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

      var init = function() {
        execute();
      };

      var execute = function() {
        var format = 'application%2Fsolr%2Bjson';
        var servlet = 'search';
        var searchURL = searchOptions.url + '/' + servlet + '?';

        searchURL += 'type=' + searchOptions.type;
        searchURL += '&facets=*';
        searchURL += '&limit=' + searchOptions.limit;

        if (searchOptions.datasetId != null) {
          searchURL += '&dataset_id=' + searchOptions.datasetId;
        }
        else {
          var tags = searchOptions.constraints.split(",");
          $.each(tags, function(i, tag) {
            var constraint = tag.split(":");
            searchURL += '&' + constraint[0] + '=' + constraint[1];
          });
        }

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



