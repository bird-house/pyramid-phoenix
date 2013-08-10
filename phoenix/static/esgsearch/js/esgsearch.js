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
    Manager.init();
    Manager.store.addByValue('distrib', 'false');
    Manager.store.addByValue('query', '*');
    Manager.doRequest();
  });

})(jQuery);
