var SimpleWPS = function(options) {
  var defaults = {
    url: null,
    process: "org.malleefowl.wms.layer",
    output: "output",
    onSuccess: function(result) { console.log('no callback defined.')},
  };
  this.options = $.extend(defaults, options);
};

$.extend(SimpleWPS.prototype, {
  execute: function() {
    var params =  {
      Request: "Execute",
      Service: "WPS",
      version: "1.0.0",
      identifier: this.options.process,
      RawDataOutput: this.options.output,
    };

    // call wps
    var me = this;
    $.get(this.options.url, params, function(result) {
      // inform about result
      me.options.onSuccess(result)
    }, 'json');
  }, 

});


