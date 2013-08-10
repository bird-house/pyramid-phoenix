var Manager;

(function ($) {

  $(function () {
    Manager = new AjaxSolr.Manager({
      // TODO: configure hostname
      solrUrl: 'http://tracy.local:8090/esg-search/'
    });
    Manager.addWidget(new AjaxSolr.ResultWidget({
      id: 'result',
      target: '#docs'
    }));
    Manager.addWidget(new AjaxSolr.PagerWidget({
      id: 'pager',
      target: '#pager',
      prevLabel: '&lt;',
      nextLabel: '&gt;',
      innerWindow: 1,
      renderHeader: function (perPage, offset, total) {
        $('#pager-header').html($('<span></span>').text('displaying ' + Math.min(total, offset + 1) + ' to ' + Math.min(total, offset + perPage) + ' of ' + total));
      }
    }));
    var fields = [ 'institute', 'experiment'];
    for (var i = 0, l = fields.length; i < l; i++) {
      Manager.addWidget(new AjaxSolr.TagcloudWidget({
        id: fields[i],
        target: '#' + fields[i],
        field: fields[i]
      }));
    }
    Manager.addWidget(new AjaxSolr.CurrentSearchWidget({
      id: 'currentsearch',
      target: '#selection'
    }));
    Manager.addWidget(new AjaxSolr.AutocompleteWidget({
      id: 'text',
      target: '#search',
      fields: [ 'institute', 'experiment']
    }));
    Manager.init();
    Manager.store.addByValue('distrib', 'false');
    //Manager.store.addByValue('query', '*');
    var params = {
      //facet: true,
      'facets': [ 'institute', 'experiment'],
      //'facet.limit': 20,
      //'facet.mincount': 1,
      //'f.topics.facet.limit': 50,
      //'json.nl': 'map'
    };
    for (var name in params) {
      Manager.store.addByValue(name, params[name]);
    }
    Manager.doRequest();
  });

})(jQuery);
