/* ESGF Dataset search */

(function($) {  
  $.extend({
    EsgDatasetSearch: function(options) {
      var defaults = {
        oid: null,
        url: null,
      };
      var searchOptions = $.extend(defaults, options);
      var selectedFacet = 'institute';
      
      var init = function() {
        init_search_options();
        init_query();
        init_constraints();
        init_facets();
        init_facet_values();
        init_time_constraints();
        init_spatial_constraints();
        search();
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
          console.log('delete');
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
        jQuery(".tm-selection").tagsManager('limitPopTags');
        search();
      };

      var selected_facet_handler = function (facet) {
        selectedFacet = facet;
        $('#search-label-category').text("Category: " + selectedFacet)
        search();
      };

      var selected_facet_value_handler = function (facet_value) {
        value = selectedFacet  + ':' + facet_value;
        jQuery(".tm-selection").tagsManager('limitPushTags');
        $(".tm-selection").tagsManager('pushTag', value);
        if (!ctrlPressed) {
          search();
        }
      };

      var update_counts = function(counts) {
        $('#tm-hit-count').text("Datesets found: " + counts);
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

        $('#' + searchOptions.oid + '-spatial').click(function () {
          search();
        });
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

      var date_format = function(date) {
        // Format a Date into a string as specified by RFC 3339.
        var month = (date.getMonth() + 1).toString();
        var dom = date.getDate().toString();
        if (month.length === 1) {
          month = '0' + month;
        }
        if (dom.length === 1) {
          dom = '0' + dom;
        }
        return date.getFullYear() + '-' + month + "-" + dom + "T12:00:00Z";
      };

      var parse_date = function(s) {
        var m;
        if ((m = s.match(/^(\d{4,4})-(\d{2,2})-(\d{2,2})T12:00:00Z$/))) {
          return new Date(m[1], m[2] - 1, m[3]);
        } else {
          return null;
        }
      };

      var init_time_constraints = function() {
        var options = { 'format': date_format, 'parse': parse_date };
        $('#' + searchOptions.oid + '-start').datepicker(options);
        $('#' + searchOptions.oid + '-start').keypress(function(e) {
          // disable ENTER
          if (e.which == 13) {
            killEvent(e);
          };
        });
        $('#' + searchOptions.oid + '-start').on('change', function(){
          search();
        });

        $('#' + searchOptions.oid + '-end').datepicker(options);
        $('#' + searchOptions.oid + '-end').keypress(function(e) {
          // disable ENTER
          if (e.which == 13) {
            killEvent(e);
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
    
      var search = function() {
        $.EsgSearch({
          url: searchOptions.url, 
          limit: 0,
          distrib: $('#' + searchOptions.oid + '-distrib').is(":checked"),
          latest: $('#' + searchOptions.oid + '-latest').is(":checked"),
          replica: $('#' + searchOptions.oid + '-replica').is(":checked"),
          query: $('#' + searchOptions.oid + '-query').val(),
          constraints: $("#" + searchOptions.oid + '-facets').val(),
          type: 'Dataset',
          temporal: $('#' + searchOptions.oid + '-temporal').is(":checked"),
          start: $('#' + searchOptions.oid + '-start').val(),
          end: $('#' + searchOptions.oid + '-end').val(),
          spatial: $('#' + searchOptions.oid + '-spatial').is(":checked"),
          bbox: $('#' + searchOptions.oid + '-bbox').val(),
          callback: function(result) { callback(result); },
        });
      };

      var callback = function(result) {
        $(".tm-facets").tagsManager('empty');
        $.each(result.facets(), function(i, tag) {
          jQuery(".tm-facets").tagsManager('limitPushTags');
          jQuery(".tm-facets").tagsManager('pushTag', tag);
        });

        $(".tm-facet").tagsManager('empty');
        $.each(result.facetValues(selectedFacet), function(i,value) {
          jQuery(".tm-facet").tagsManager('limitPushTags');
          jQuery(".tm-facet").tagsManager('pushTag', value);
        });
          
        update_counts(result.numFound());
      };

      init();
    },
  });
})(jQuery);


/* ESGF File/Aggregation Search */

(function($) {  
  $.extend({
    EsgFileSearch: function(options) {
      var defaults = {
        oid: null,
        url: null,
        distrib: true,
        latest: true,
        replica: false,
        query: '*',
        constraints: 'project:CMIP5,product:output1',
        limit: 5,
        temporal: false,
        start: null,
        end: null,
        spatial: false,
        bbox: null,
        type: 'File',
      };
      var searchOptions = $.extend(defaults, options);
      var count = 0;
      var topicContainer = $('ul#' + searchOptions.oid + '-choices');

      var init = function() {
        count = 0;
        topicContainer.empty();
        execute();
      };

      var updateDataset = function(id) {
        topicContainer.append(
          $(document.createElement('h4')).text('Dateset ' + id)
        );
      };

      var updateFiles = function(values) {
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
                $(document.createElement('span')).text(title)
              )
              .append(
                $(document.createElement('p'))
              ))
          count = count + 1;
        });
      };

      var execute = function() {
        $.EsgSearch({
          url: searchOptions.url,
          type: 'Dataset',
          fields: 'id,title,number_of_files,number_of_aggregations',
          limit: searchOptions.limit,
          constraints: searchOptions.constraints,
          distrib: searchOptions.distrib,
          latest: searchOptions.latest,
          replica: searchOptions.replica,
          query: searchOptions.query,
          temporal: searchOptions.temporal,
          start: searchOptions.start,
          end: searchOptions.end,
          spatial: searchOptions.spatial,
          bbox: searchOptions.bbox,
          callback: function(result) {  _execute(result) },
        });
      };

      var _execute = function(result) {
        $.each(result.docs(), function(i, doc) {
          console.log(doc.title);
          var limit = doc.number_of_files;
          if (searchOptions.type == 'Aggregation') {
            limit = doc.number_of_aggregations;
          }
          $.EsgSearch({
            url: searchOptions.url,
            type: searchOptions.type,
            datasetId: doc.id,
            constraints: searchOptions.constraints,
            limit: limit,
            distrib: searchOptions.distrib,
            latest: searchOptions.latest,
            replica: searchOptions.replica,
            callback: function(result) {  updateDataset(doc.title); callback(result); },
          });
        });
      };

      var callback = function(result) {
        var values = {};
        $.each(result.docs(), function(i, doc) {
          //console.log(doc.title);
          var url = result.url(doc, searchOptions.type);
          //console.log(url);
          var title = doc.title
          var size = parseInt(doc.size);
          if ( !isNaN(size) ) {
            size = Math.floor(doc.size/(1024*1024));
            title = title + ' (' + size + ' MB)';
          }
          if (url != null) {
            var start = new Date(searchOptions.start);
            var end = new Date(searchOptions.end);
         
            if (_withinDateRange(start, end, doc)) {
              values[url] = title;
            }
          }
        });
        updateFiles(values);
      };

      var _withinDateRange = function(start, end, doc) {
        var fileDates = _dateFromId(doc.instance_id);
        if (fileDates[0].getFullYear() <= start.getFullYear() && 
            fileDates[0].getMonth() <= start.getMonth() && 
            fileDates[0].getDate() <= start.getDate() && 
            fileDates[1].getFullYear() >= end.getFullYear() && 
            fileDates[1].getMonth() >= end.getMonth() && 
            fileDates[1].getDate() >= end.getDate() ) {
          return true;
        }

        return false;
      };

      var _dateFromId = function(id) {
        var txt = id.split('_').pop();
        txt = txt.split('.')[0];
        var parts = txt.split('-');
        var start = parts[0];
        var end = parts[1];
        //console.log(start + ' - ' + end);
        var startDate = _strToDate(start);
        var endDate = _strToDate(end);

        return [startDate, endDate];
      };

      var _strToDate = function(str) {
        var year = str.substring(0,4);
        var month = str.substring(4,6);
        var day = str.substring(6,8);
        var date = new Date(year, month - 1, day);
        //console.log(date);
        return date;
      };

      init();
    },
  });
})(jQuery);



