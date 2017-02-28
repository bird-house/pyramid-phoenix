var EsgSearchResult = function(json) {
  this._json = json;
  this._facets = null;
};

$.extend(EsgSearchResult.prototype, {

  numFound: function() {
    return this._json.numFound;
  },

  facets: function() {
    return this._json.facets;
  },

  pinnedFacets: function() {
    return this._json.pinnedFacets;
  },

  facetValues: function(facet) {
    return this._json.facetValues;
  },

});


(function($) {
  $.extend({
    EsgSearch: function(options) {
      var defaults = {
        url: null,
        selected: 'project',
        query: '*:*',
        constraints: null,
        limit: 0,
        facets: '*',
        fields: '*',
        distrib: true,
        latest: true,
        replica: false,
        temporal: false,
        start: '',
        end: '',
        callback: function(result) { console.log('no callback defined.')},
      };
      var searchOptions = $.extend(defaults, options);

      var execute = function() {
        search(buildQuery());
      };

      var search = function(query) {
        var servlet = 'search';
        var searchURL = searchOptions.url + '/' + servlet + '?';
        searchURL += query;

        $.getJSON(searchURL, function(json) {
          var result = new EsgSearchResult(json);
          searchOptions.callback(result);
        });
      };

      var buildQuery = function() {
        var query = '';
        query += 'selected=' + searchOptions.selected;
        query += '&facets=' + searchOptions.facets;
        query += '&fields=' + searchOptions.fields;
        query += '&limit=' + searchOptions.limit;
        query += '&constraints=' + searchOptions.constraints;

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

        return query;
      };

      execute();
    },
  });
})(jQuery);
