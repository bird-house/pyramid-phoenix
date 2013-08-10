(function ($) {

AjaxSolr.AutocompleteWidget = AjaxSolr.AbstractTextWidget.extend({
 
  afterRequest: function () {
    $(this.target).find('input').unbind().removeData('events').val('');

    var self = this;

    var callback = function (response) {
      var list = [];
      for (var i = 0; i < self.fields.length; i++) {
        var field = self.fields[i];
	var counts = [];
	for (var i = 0, l = response.facet_counts.facet_fields[field].length; i < l; i += 2) {
	  counts.push({
            facet: response.facet_counts.facet_fields[field][i],
            count: parseInt(response.facet_counts.facet_fields[field][i+1])
	  });
	}
	for (var i = 0, l = counts.length; i < l; i++) {
	  facet = counts[i].facet
	  count = counts[i].count
          list.push({
            field: field,
            value: facet,
            label: facet + ' (' + count + ') - ' + field
          });
        }
      }

      self.requestSent = false;
      $(self.target).find('input').autocomplete('destroy').autocomplete({
        source: list,
        select: function(event, ui) {
          if (ui.item) {
            self.requestSent = true;
            if (self.manager.store.addByValue('fq', ui.item.field + ':' + AjaxSolr.Parameter.escapeValue(ui.item.value))) {
              self.doRequest();
            }
          }
        }
      });

      // This has lower priority so that requestSent is set.
      $(self.target).find('input').bind('keydown', function(e) {
        if (self.requestSent === false && e.which == 13) {
          var value = $(this).val();
          if (value && self.set(value)) {
            self.doRequest();
          }
        }
      });
    } // end callback

    //var params = [ 'rows=0&facet=true&facet.limit=-1&facet.mincount=1&json.nl=map' ];
    var params = [ 'distrib=false'];
    /*for (var i = 0; i < this.fields.length; i++) {
      params.push('facet.field=' + this.fields[i]);
    }*/
    /*var values = this.manager.store.values('fq');
    for (var i = 0; i < values.length; i++) {
      params.push('fq=' + encodeURIComponent(values[i]));
    }*/
    //params.push('q=' + this.manager.store.get('query').val());
    string = this.manager.store.esgsearchString()
    $.getJSON(this.manager.solrUrl + 'search?' + string + '&format=application%2Fsolr%2Bjson', {}, callback);

    //$.getJSON(this.manager.solrUrl + 'select?' + params.join('&') + '&wt=json&json.wrf=?', {}, callback);
  }
});

})(jQuery);
