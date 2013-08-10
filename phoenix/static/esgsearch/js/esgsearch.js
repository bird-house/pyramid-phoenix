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
    Manager.init();
    Manager.store.addByValue('distrib', 'false');
    Manager.store.addByValue('query', '*');
    Manager.doRequest();
  });

})(jQuery);
