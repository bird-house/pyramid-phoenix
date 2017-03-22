/* ESGF Dataset search */

(function($) {
  $.extend({
    EsgDatasetSearch: function(options) {
      var defaults = {
        oid: null,
        url: null,
        constraints: null,
        categories: null,
        keywords: null,
        pinnedFacets: null,
        selectedFacet: 'project',
      };
      var searchOptions = $.extend(defaults, options);
      var selectedFacet = searchOptions.selectedFacet;

      var init = function() {
        initDatasetCollapse();
        init_toggle_collapse();
        init_search_options();
        init_query();
        init_constraints();
        init_facets();
        init_facet_values();
        init_pinned_facets();
        init_time_constraints();
        //init_spatial_constraints();
        //search();
      };

      var initDatasetCollapse = function() {
        $('.dataset').on('show.bs.collapse', function () {
          var _el = $(this);
          var dataset_id = $(this).find('.files').attr('id');
          var waitDialog = $('#please-wait-dialog');
          waitDialog.modal('show');
          $.getJSON(buildFileSearchQuery(dataset_id), function(result) {
            text = '';
            $.each(result.files, function(i, file) {
              text += '<li class="list-group-item">';
              text += '<span class="list-group-item-heading">';
              text += '<btn';
              text += ' class="btn btn-default btn-xs pull-right';
              if (file.is_in_cart) {
                text += ' btn-cart-remove"';
                text += ' title="Remove from Cart"';
              } else {
                text += ' btn-cart-add"';
                text += ' title="Add to Cart"';
              }
              text += ' data-toggle="tooltip"';
              text += ' data-value="' + file.opendap_url + '"';
              text += ' data-type="application/x-ogc-dods"';
              text += ' role="button">';
              text += '<icon class="fa fa-lg';
              if (file.is_in_cart) {
                text += ' fa-times">';
              } else {
                text += ' fa-cart-plus">';
              }
              text += '</icon>';
              text += '</btn>';
              text += file.filename;
              text += '</span>';
              text += '<p class="list-group-item-text">';
              text += '<a href="' + file.download_url + '" target="_">';
              text += '<i class="fa fa-download"></i> Download </a>';
              text += '<a href="' + file.opendap_url + '".html target="_">';
              text += '<i class="fa fa-cube"></i> OpenDAP </a>';
              text += '</p>';
              text += '</li>';
            });
            _el.find('.files').html(text);
            waitDialog.modal('hide');
          });
        })
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

      var numTags = function(tags) {
        var result = 1;
        if (tags != '') {
          result = tags.split(',').length;
        }
        return result;
      };

      /*
      var update_counts = function(counts) {
        $('#tm-hit-count').text("Total: " + counts);
        $('#' + searchOptions.oid + '-hit-count').val(counts);
      };
      */

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
          hiddenTagListId: searchOptions.oid + '-constraints',
          deleteHandler: deleted_constraint_handler,
          prefilled: searchOptions.constraints,
          maxTags: numTags(searchOptions.constraints),
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
          prefilled: searchOptions.categories,
          maxTags: numTags(searchOptions.categories),
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
          prefilled: searchOptions.keywords,
          maxTags: numTags(searchOptions.keywords),
        });
      };

      var init_pinned_facets = function() {
        $(".tm-pinned-facets").tagsManager({
          //prefilled: ["hello"],
          preventSubmitOnEnter: true,
          delimiters: [9, 13, 44],
          tagClass: 'tm-tag tm-tag-disabled',
          isSelectable: false,
          prefilled: searchOptions.pinnedFacets,
          maxTags: numTags(searchOptions.pinnedFacets),
        });
      };

      var buildSearchQuery = function() {
        var searchURL = searchOptions.url + '?';
        var query = searchURL;
        query += 'selected=' + selectedFacet;
        query += '&constraints=' + $("#" + searchOptions.oid + '-constraints').val();

        // search options
        if ($('#' + searchOptions.oid + '-distrib').is(":checked") == true) {
          query += '&distrib=true';
        } else {
          query += '&distrib=false';
        }
        if ($('#' + searchOptions.oid + '-latest').is(":checked") == true) {
          query += '&latest=true';
        } else {
          query += '&latest=false';
        }
        if ($('#' + searchOptions.oid + '-replica').is(":checked") == true) {
          query += '&replica=true';
        } else {
          query += '&replica=false';
        }

        // query option
        query += '&query=' + $('#' + searchOptions.oid + '-query').val();
        // date options
        if ($('#' + searchOptions.oid + '-temporal').is(":checked") == true) {
          query += '&start=' + $('#' + searchOptions.oid + '-start').val();
          query += '&end=' + $('#' + searchOptions.oid + '-end').val();
        }

        return query;
      };

      var buildFileSearchQuery = function(dataset_id) {
        var query = "/esgfsearch/files?dataset_id=" + dataset_id;
        // search options
        if ($('#' + searchOptions.oid + '-distrib').is(":checked") == true) {
          query += '&distrib=true';
        } else {
          query += '&distrib=false';
        }
        if ($('#' + searchOptions.oid + '-latest').is(":checked") == true) {
          query += '&latest=true';
        } else {
          query += '&latest=false';
        }
        if ($('#' + searchOptions.oid + '-replica').is(":checked") == true) {
          query += '&replica=true';
        } else {
          query += '&replica=false';
        }
        // date options
        if ($('#' + searchOptions.oid + '-temporal').is(":checked") == true) {
          query += '&start=' + $('#' + searchOptions.oid + '-start').val();
          query += '&end=' + $('#' + searchOptions.oid + '-end').val();
        }
        return query;
      };

      var search = function() {
        query = buildSearchQuery();
        // alert("run search: " + query);
        window.location = query;

        /*
        $.getJSON(buildQuery(), function(result) {
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
        });
        */
      };

      init();
    },
  });
})(jQuery);
