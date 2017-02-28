/* ESGF Dataset search */

(function($) {
  $.extend({
    EsgDatasetSearch: function(options) {
      var defaults = {
        oid: null,
        url: null,
      };
      var searchOptions = $.extend(defaults, options);
      var selectedFacet = 'project';

      var init = function() {
        init_toggle_collapse();
        init_search_options();
        init_query();
        init_constraints();
        init_facets();
        init_facet_values();
        init_pinned_facets();
        init_time_constraints();
        //init_spatial_constraints();
        search();
      };

      var init_toggle_collapse = function() {
        $('a[data-toggle="collapse"]').click(function () {
          $(this).find('i').toggleClass('fa-chevron-right fa-chevron-down');
        })
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
          search();
        }
      });

      // using delete to remove selections of current category
      $(window).keydown(function(e) {
        if (e.which == 46) { // delete
          $(".tm-selection").tagsManager('empty');
          search();
        }
      });

      var killEvent = function (e) {
        e.cancelBubble = true;
        e.returnValue = false;
        e.stopPropagation();
        e.preventDefault();
      };

      var deleted_constraint_handler = function(constraint) {
        $(".tm-selection").tagsManager('limitPopTags');
        search();
      };

      var selected_facet_handler = function (facet) {
        selectedFacet = facet;
        $('#search-label-category').text("KEYWORDS: " + selectedFacet)
        search();
      };

      var selected_facet_value_handler = function (facet_value) {
        value = selectedFacet  + ':' + facet_value;
        $(".tm-selection").tagsManager('limitPushTags');
        $(".tm-selection").tagsManager('pushTag', value);
        if (!ctrlPressed) {
          search();
        }
      };

      var update_counts = function(counts) {
        $('#tm-hit-count').text("Total: " + counts);
        $('#' + searchOptions.oid + '-hit-count').val(counts);
      };

      var init_search_options = function() {
        $('#' + searchOptions.oid + '-distrib').click(function () {
          search();
        });

        $('#' + searchOptions.oid + '-replica').click(function () {
          search();
        });

        $('#' + searchOptions.oid + '-latest').click(function () {
          search();
        });

        $('#' + searchOptions.oid + '-temporal').click(function () {
          search();
        });

        /*
        $('#' + searchOptions.oid + '-spatial').click(function () {
          search();
        });
        */
      };

      var init_query = function() {
        $('#' + searchOptions.oid + '-query').keypress(function(e) {
          // disable ENTER
          if (e.which == 13) {
            killEvent(e);
            search();
          };
        });
      };

      var init_time_constraints = function() {
        // start year
        $('#' + searchOptions.oid + '-start').keypress(function(e) {
          // disable ENTER and run search
          if (e.which == 13) {
            killEvent(e);
            search();
          };
        });
        $('#' + searchOptions.oid + '-start').on('change', function(){
          search();
        });

        // end year
        $('#' + searchOptions.oid + '-end').keypress(function(e) {
          // disable ENTER and run search
          if (e.which == 13) {
            killEvent(e);
            search();
          };
        });
        $('#' + searchOptions.oid + '-end').on('change', function(){
          search();
        });
      };

      var init_constraints = function() {
        $(".tm-selection").tagsManager({
          preventSubmitOnEnter: true,
          delimiters: [9, 13, 44],
          //maxTags: 2,
          tagClass: 'tm-tag tm-tag-success',
          hiddenTagListId: searchOptions.oid + '-facets',
          deleteHandler: deleted_constraint_handler,
        });
      };

      var init_spatial_constraints = function() {
        $('#' + searchOptions.oid + '-bbox').keypress(function(e) {
          // disable ENTER
          if (e.which == 13) {
            killEvent(e);
            search();
          };
        });
        $('#' + searchOptions.oid + '-bbox').on('change', function(){
          search();
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

      var init_pinned_facets = function() {
        $(".tm-pinned-facets").tagsManager({
          //prefilled: ["hello"],
          preventSubmitOnEnter: true,
          delimiters: [9, 13, 44],
          tagClass: 'tm-tag tm-tag-disabled',
          isSelectable: false,
        });
      };

      var search = function() {
        $.EsgSearch({
          url: searchOptions.url,
          selected: selectedFacet,
          limit: 10,
          facets: "*",
          distrib: $('#' + searchOptions.oid + '-distrib').is(":checked"),
          latest: $('#' + searchOptions.oid + '-latest').is(":checked"),
          replica: $('#' + searchOptions.oid + '-replica').is(":checked"),
          query: $('#' + searchOptions.oid + '-query').val(),
          constraints: $("#" + searchOptions.oid + '-facets').val(),
          temporal: $('#' + searchOptions.oid + '-temporal').is(":checked"),
          start: $('#' + searchOptions.oid + '-start').val() + '-01-01T12:00:00Z',
          end: $('#' + searchOptions.oid + '-end').val()  + '-12-31T12:00:00Z',
          //spatial: $('#' + searchOptions.oid + '-spatial').is(":checked"),
          //bbox: $('#' + searchOptions.oid + '-bbox').val(),
          callback: function(result) { callback(result); },
        });
      };

      var callback = function(result) {
        $(".tm-facets").tagsManager('empty');
        $.each(result.facets, function(i, tag) {
          $(".tm-facets").tagsManager('limitPushTags');
          $(".tm-facets").tagsManager('pushTag', tag);
        });

        $(".tm-facet").tagsManager('empty');
        $.each(result.facetValues, function(i,value) {
          $(".tm-facet").tagsManager('limitPushTags');
          $(".tm-facet").tagsManager('pushTag', value);
        });

        $(".tm-pinned-facets").tagsManager('empty');
        $.each(result.pinnedFacets, function(i, tag) {
          selection = $("#" + searchOptions.oid + '-facets').val();
          if (selection.indexOf(tag) < 0) {
            $(".tm-pinned-facets").tagsManager('limitPushTags');
            $(".tm-pinned-facets").tagsManager('pushTag', tag);
          }
        });

        update_counts(result.numFound);
      };

      init();
    },
  });
})(jQuery);
