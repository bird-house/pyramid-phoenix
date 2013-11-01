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

      var updateChoices = function(values) {
        var topicContainer = $('ul#' + searchOptions.oid + '-choices');
        topicContainer.empty();
        var count = 0;
        $.each(values, function (value, title) {
          topicContainer.append(
            $(document.createElement("li"))
              .append(
                $(document.createElement("input")).attr({
                  type: 'checkbox',
                  id: searchOptions.oid + '-' + count,
                  name: count,
                  value: value
                })
              )
              .append(
                $(document.createElement('label')).attr({
                  'for': searchOptions.oid + '-' + count
                })
                  .text(title)
              ))
          count = count + 1;
          console.log(title);
        });
      };

      var execute = function() {
        var format = 'application%2Fsolr%2Bjson';
        var servlet = 'search';
       
        var searchURL = searchOptions.url + '/' + servlet + '?';
        searchURL += 'type=Dataset';
        searchURL += '&facets=id';
        var tags = searchOptions.constraints.split(",");
        var constraints = '';
        $.each(tags, function(i, tag) {
          var constraint = tag.split(":");
          constraints += '&' + constraint[0] + '=' + constraint[1];
        });
        searchURL += constraints;
        searchURL += '&limit=0';
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
        var ds_ids = [];
        $.getJSON(searchURL, function(json) {
          var counts = json.facet_counts.facet_fields['id'];
          $.each(counts, function(i, value) {
            if (i % 2 == 0) {
              ds_ids.push(value);
            }
          });
          //console.log('ids1: ' + ds_ids);
          _execute(ds_ids);
        });
      };

      var _execute = function(ds_ids) {
        //console.log('ds_ids: ' + ds_ids);

        var format = 'application%2Fsolr%2Bjson';
        var servlet = 'search';
       
        var searchURL = searchOptions.url + '/' + servlet + '?';
        searchURL += 'type=' + searchOptions.type;
        searchURL += '&facets=*';
        searchURL += '&dataset_id=' + ds_ids[0];
        var tags = searchOptions.constraints.split(",");
        var constraints = '';
        $.each(tags, function(i, tag) {
          var constraint = tag.split(":");
          if (constraint[0] == 'variable') {
            constraints += '&' + constraint[0] + '=' + constraint[1];
          }
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
        //searchURL += '&query=' +  searchOptions.query;

        console.log(searchURL);
        $.getJSON(searchURL, function(json) {
          var facet_counts = json.facet_counts.facet_fields;
          var facets = [];
          $.each(facet_counts, function(tag, values) {
            if (values.length > 2) {
              facets.push(tag);
            }
          });
          var docs = json.response.docs;
          var values = {};
          $.each(docs, function(i, doc) {
            console.log(doc.title);
            var url = null;
            var serviceType = 'HTTPServer';
            if (searchOptions.type == 'Aggregation') {
              serviceType = 'OPENDAP';
            }
            $.each(doc.url, function(i, encoded) {
              var service = encoded.split("|");
              if (service[2] == serviceType) {
                url = service[0];
              };
            });
            console.log(url);
            values[url] = doc.title;
          });
          console.log(values);
          updateChoices(values);
        });
      };

      init();
    },
  });
})(jQuery);