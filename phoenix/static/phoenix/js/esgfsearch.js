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
        pinnedKeywords: null,
        selectedCategory: 'project',
        bbox: null,
      };
      var searchOptions = $.extend(defaults, options);
      var selectedCategory = searchOptions.selectedCategory;

      var init = function() {
        initDatasetCollapse();
        initToggleCollapse();
        initSearchOptions();
        initQuery();
        initConstraints();
        initCategories();
        initKeywords();
        initPinnedKeywords();
        initTimeExtent();
        initBBoxExtent();
      };

      var _buildListGroupItem = function(item) {
        var color = 'info';
        if (item.type == 'Aggregation') {
          color = 'success';
        }
        var text = '<li class="list-group-item list-group-item-' + color + '">';
        text += '<span class="list-group-item-heading">';
        if (item.cart_available) {
          text += '<btn';
          text += ' class="btn btn-outline-secondary btn-sm float-end';
          if (item.is_in_cart) {
            text += ' btn-cart-remove"';
            text += ' title="Remove from Cart"';
          } else {
            text += ' btn-cart-add"';
            text += ' title="Add to Cart"';
          }
          text += ' data-toggle="tooltip"';
          text += ' data-value="' + item.opendap_url + '"';
          text += ' data-type="application/x-ogc-dods"';
          text += ' role="button">';
          text += '<icon class="fa fa-lg';
          if (item.is_in_cart) {
            text += ' fa-times">';
          } else {
            text += ' fa-cart-plus">';
          }
          text += '</icon>';
          text += '</btn>';
        }
        text += item.title;
        text += '</p>';
        text += item.abstract;
        text += '</span>';
        text += '<p class="list-group-item-text">';
        if (item.download_url) {
          text += '<a href="' + item.download_url + '" target="_">';
          text += '<i class="fa fa-download"></i> Download </a>';
        }
        if (item.opendap_url) {
          text += '<a href="' + item.opendap_url + '.html' + '" target="_">';
          text += '<i class="fa fa-cube"></i> OpenDAP </a>';
        }
        /*
        text += '<a href="" target="_">';
        text += '<i class="fa fa-info"></i> Info </a>';
        */
        text += '</p>';
        text += '</li>';
        return text;
      };

      var initDatasetCollapse = function() {
        $('.dataset').on('show.bs.collapse', function () {
          var _el = $(this);
          var dataset_id = $(this).find('.items').attr('dataset_id');
          var waitDialog = $('#please-wait-dialog');
          waitDialog.modal('show');
          // fill dataset items
          $.getJSON(buildItemsSearchQuery(dataset_id), function(result) {
            var html = '';
            $.each(result.items, function(i, item) {
              html += _buildListGroupItem(item);
            });
            _el.find('.items').html(html);
            waitDialog.modal('hide');
          });
        })
      };

      var initToggleCollapse = function() {
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
        selectedCategory = facet;
        $('#search-label-category').text("KEYWORDS: " + selectedCategory)
        search();
      };

      var selected_facet_value_handler = function (facet_value) {
        value = selectedCategory  + ':' + facet_value;
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

      var initSearchOptions = function() {
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
      };

      var initQuery = function() {
        $('#' + searchOptions.oid + '-query').keypress(function(e) {
          // disable ENTER
          if (e.which == 13) {
            killEvent(e);
            search();
          };
          $('#' + searchOptions.oid + '-query').on('change', function(){
            search();
          });
        });
      };

      var initTimeExtent = function() {
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

      var initConstraints = function() {
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

      var initBBoxExtent = function() {
        var map = L.map('map', {
          center: [0, 0],
          zoom: 0,
          zoomControl: false,
        });  // map
        // base layer
        L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png?{foo}', {foo: 'bar'}).addTo(map);
        map.on('moveend', function() {
          searchOptions.bbox = map.getBounds().toBBoxString();
          //search();
        });

      };   // bbox extent

      var initCategories = function() {
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

      var initKeywords = function() {
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

      var initPinnedKeywords = function() {
        $(".tm-pinned-facets").tagsManager({
          //prefilled: ["hello"],
          preventSubmitOnEnter: true,
          delimiters: [9, 13, 44],
          tagClass: 'tm-tag tm-tag-disabled',
          isSelectable: false,
          prefilled: searchOptions.pinnedKeywords,
          maxTags: numTags(searchOptions.pinnedKeywords),
        });
      };

      var _buildQuery = function(baseURL) {
        var query = baseURL;
        // constraints
        query += '&constraints=' + $("#" + searchOptions.oid + '-constraints').val();
        // distrib option
        if ($('#' + searchOptions.oid + '-distrib').is(":checked") == true) {
          query += '&distrib=true';
        } else {
          query += '&distrib=false';
        }
        // latest option
        if ($('#' + searchOptions.oid + '-latest').is(":checked") == true) {
          query += '&latest=true';
        } else {
          query += '&latest=false';
        }
        // replica option
        if ($('#' + searchOptions.oid + '-replica').is(":checked") == true) {
          query += '&replica=true';
        } else {
          query += '&replica=false';
        }
        // freetext search
        query += '&query=' + $('#' + searchOptions.oid + '-query').val();
        // date options
        if ($('#' + searchOptions.oid + '-temporal').is(":checked") == true) {
          query += '&temporal=true';
        } else {
          query += '&temporal=false';
        }
        query += '&start=' + $('#' + searchOptions.oid + '-start').val();
        query += '&end=' + $('#' + searchOptions.oid + '-end').val();
        return query;
      }

      var buildDatasetSearchQuery = function() {
        var searchURL = searchOptions.url + '?';
        searchURL += 'selected=' + selectedCategory;
        return _buildQuery(searchURL);
      };

      var buildItemsSearchQuery = function(dataset_id) {
        var searchURL = "/esgfsearch/items?";
        searchURL += "dataset_id=" + dataset_id;
        return _buildQuery(searchURL);
      };

      var search = function() {
        query = buildDatasetSearchQuery();
        window.location = query;
      };

      init();
    },
  });
})(jQuery);
