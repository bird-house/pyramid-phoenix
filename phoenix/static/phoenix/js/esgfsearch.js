var EsgSearchResult = function(json) {
  this._json = json;
  this._facets = null;
};

$.extend(EsgSearchResult.prototype, {
  raw: function() {
    return this._json;
  },

  numFound: function() {
    return this._json.response.numFound;
  },

  facets: function() {
    if (this._facets == null) {
      var facets = [];
      var facet_counts = this._json.facet_counts.facet_fields;
      $.each(facet_counts, function(tag, values) {
        if (values.length > 2) {
          facets.push(tag);
        }
      });
      this._facets = facets.sort();
    }
    return this._facets;
  },

  pinnedFacets: function() {
    var facets = [];
    var facet_counts = this._json.facet_counts.facet_fields;
    $.each(facet_counts, function(tag, values) {
      if (values.length == 2) {
        facets.push(tag + ":" + values[0]);
      }
    });
    return facets.sort();
  },

  facetValues: function(facet) {
    var counts = this._json.facet_counts.facet_fields[facet];
    var facet_values = [];
    $.each(counts, function(i,value) {
      if (i % 2 == 0) {
        facet_values.push(value);
      }
    });
    return facet_values.sort();
  },

  docs: function() {
    return this._json.response.docs;
  },

  url: function(doc, type) {
    var url = null;
    var serviceType = 'HTTPServer';
    if (type == 'Aggregation') {
      serviceType = 'OPENDAP';
    }
    $.each(doc.url, function(i, encoded) {
      var service = encoded.split("|");
      //console.log('service: ' + service[2]);
      if (service[2] == serviceType) {
        url = service[0];
      };
      if (serviceType == 'OPENDAP' && url != null) {
        url = url.replace('.html', '');
      }
    });

    //console.log('url: ' + url);
    return url;
  },
});


(function($) {
  $.extend({
    EsgSearch: function(options) {
      var defaults = {
        url: null,
        query: '*:*', // TODO: rename query to freetext
        datasetId: null,
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
        spatial: false,
        bbox: '',
        type: 'Dataset',
        callback: function(result) { console.log('no callback defined.')},
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
          var result = new EsgSearchResult(json);
          searchOptions.callback(result);
        });
      };

      var buildQuery = function() {
        var query = '';

        query += 'type=' + searchOptions.type;
        query += '&facets=' + searchOptions.facets;
        query += '&fields=' + searchOptions.fields;
        query += '&limit=' + searchOptions.limit;

        if (searchOptions.datasetId != null) {
          query += '&dataset_id=' + searchOptions.datasetId;
        }

        var tags = searchOptions.constraints.split(",");
        $.each(tags.sort(), function(i, tag) {
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

        //console.log(query);
        return query;
      };

      execute();
    },
  });
})(jQuery);
