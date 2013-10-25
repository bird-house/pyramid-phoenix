(function($) {  
  $.extend({
    EsgSearch: function(options) {
      var defaults = {
        oid: null,
        url: null,
        query: '*',
        distrib: 'true',
        latest: 'true',
        replica: 'false',
        constraints: null,
        type: 'Dataset',
      };
      var searchOptions = $.extend(defaults, options);
      var selectedFacet = 'institute';
      
      var init = function() {
        init_search_options();
        init_query();
        init_constraints();
        init_facets();
        init_facet_values();
        execute();
      };

      // using ctrl for multiple selection of facets
      var ctrlPressed = false;
      $(window).keydown(function(e) {
        if (e.which == 17) { // ctrl
          ctrlPressed = true;
        }
      }).keyup(function(e) {
        if (e.which == 17) { // ctrl
          ctrlPressed = false;
          execute();
        }
      });

      // using delete to remove selections of current category
      $(window).keydown(function(e) {
        if (e.which == 46) { // delete
          console.log('delete');
          $(".tm-selection").tagsManager('empty');
          execute();
        }
      });

      var killEvent = function (e) {
        e.cancelBubble = true;
        e.returnValue = false;
        e.stopPropagation();
        e.preventDefault();
      };

      var deleted_constraint_handler = function(constraint) {
        jQuery(".tm-selection").tagsManager('limitPopTags');
        execute();
      };

      var selected_facet_handler = function (facet) {
        selectedFacet = facet;
        $('#search-label-category').text("Category: " + selectedFacet)
        execute();
      };

      var selected_facet_value_handler = function (facet_value) {
        value = selectedFacet  + ':' + facet_value;
        jQuery(".tm-selection").tagsManager('limitPushTags');
        $(".tm-selection").tagsManager('pushTag', value);
        if (!ctrlPressed) {
          execute();
        }
      };

      var update_counts = function(counts) {
        $('#search-label-counts').text("Datasets found: " + counts)
      };

      var init_search_options = function() {
        check_search_options();

        $('#' + searchOptions.oid + '-cb-distrib').click(function () {
          var thisCheck = $(this);
          check_search_options();
          execute();
        });

        $('#' + searchOptions.oid + '-cb-replica').click(function () {
          check_search_options();
          execute();
        });

        $('#' + searchOptions.oid + '-cb-all-versions').click(function () {
          check_search_options();
          execute();
        });
      };

      var check_search_options = function() {
        searchOptions.distrib = '' + $('#' + searchOptions.oid + '-cb-distrib').is(":checked");
        searchOptions.replica = 'false';
        if ($('#' + searchOptions.oid + '-cb-replica').is(":checked")) {
          searchOptions.replica = null;
        }
        searchOptions.latest = 'true';
        if ($('#' + searchOptions.oid + '-cb-all-versions').is(":checked")) {
          searchOptions.latest = null;
        }
      };

      var init_query = function() {
        $('#' + searchOptions.oid + '-query').keypress(function(e) {
          // disable ENTER
          if (e.which == 13) {
            killEvent(e);
            execute();
          };
        });
      };

      var init_constraints = function() {
        $(".tm-selection").tagsManager({
          prefilled: searchOptions.constraints,
          preventSubmitOnEnter: true,
          delimiters: [9, 13, 44],
          //maxTags: 2,
          tagClass: 'tm-tag tm-tag-success',
          hiddenTagListId: searchOptions.oid + '-facets',
          deleteHandler: deleted_constraint_handler,
        });
      };

      var init_facets = function() {
        $(".tm-facets").tagsManager({
          //prefilled: ["hello"],
          preventSubmitOnEnter: true,
          delimiters: [9, 13, 44],
          //maxTags: 1,
          tagClass: 'tm-tag tm-tag-info',
          isSelectable: true,
          selectHandler: selected_facet_handler,
        });
      };

      var init_facet_values = function() {
        $(".tm-facet").tagsManager({
          //prefilled: ["MPI-M", "NCC", "MIROC", "BCC"],
          preventSubmitOnEnter: true,
          delimiters: [9, 13, 44],
          //maxTags: 4,
          tagClass: 'tm-tag tm-tag-warning tm-tag-mini',
          isSelectable: true,
          selectHandler: selected_facet_value_handler,
        });
      };
    
      var execute = function() {
        var limit = '0';
        var format = 'application%2Fsolr%2Bjson';
        var constraints = ''; //&project=CMIP5
        var servlet = 'search';
        var tags = $("#" + searchOptions.oid + '-facets').val().split(",");
        $.each(tags, function(i, tag) {
          var constraint = tag.split(":");
          constraints += '&' + constraint[0] + '=' + constraint[1];
        });

        var searchURL = searchOptions.url + '/' + servlet + '?';
        searchURL += 'type=' + searchOptions.type;
        searchURL += '&facets=*';
        searchURL += constraints; 
        searchURL += '&limit=' + limit;
        if ( searchOptions.distrib != null ) {
          searchURL += '&distrib=' + searchOptions.distrib;
        }
        if ( searchOptions.latest != null ) {
          searchURL += '&latest=' + searchOptions.latest; 
        }
        if (searchOptions.replica != null ) {
          searchURL += '&replica=' + searchOptions.replica; 
        }
        searchURL += '&format=' + format;
        searchURL += '&query=' +  $('#' + searchOptions.oid + '-query').val();

        // alert(searchURL);
        $.getJSON(searchURL, function(json) {
          var facet_counts = json.facet_counts.facet_fields;
          var facets = [];
          $.each(facet_counts, function(tag, values) {
            if (values.length > 2) {
              facets.push(tag);
            }
          });
          $(".tm-facets").tagsManager('empty');
          $.each(facets.sort(), function(i, tag) {
            jQuery(".tm-facets").tagsManager('limitPushTags');
            jQuery(".tm-facets").tagsManager('pushTag', tag);
          });
          var counts = json.facet_counts.facet_fields[selectedFacet];
          $(".tm-facet").tagsManager('empty');
          var facet_values = [];
          $.each(counts, function(i,value) {
            if (i % 2 == 0) {
              facet_values.push(value);
            }
          });
          $.each(facet_values.sort(), function(i,value) {
            jQuery(".tm-facet").tagsManager('limitPushTags');
            jQuery(".tm-facet").tagsManager('pushTag', value);
          });
          
          update_counts(json.response.numFound);
        });
      };

      init();
    },
  });
})(jQuery);



