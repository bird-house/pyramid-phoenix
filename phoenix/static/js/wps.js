var SimpleWPS = function(options) {
 
  var defaults = {
    url: "/wps",
    process: null,
    output: "output",
    raw: true,
    format: 'json',
    onSuccess: function(result) { console.log('no callback defined.')},
  };
  this.options = $.extend(defaults, options);
};

$.extend(SimpleWPS.prototype, {
  execute: function(inputs=[]) {
    var params =  {
      Request: "Execute",
      Service: "WPS",
      version: "1.0.0",
      identifier: this.options.process,
    
    };
    if (this.options.raw) {
      params.RawDataOutput=this.options.output;
    }
    else {
      params.ResponseDocument=this.options.output;// + "@asReference=true"; 
      params.storeExecuteResponse=true;
      params.status=false;
    }

    dataInputs = ''
    $.each(inputs, function(key, value) {
      dataInputs += key + '=' + value + ';'
    });
    params.dataInputs = dataInputs;
    // call wps
    var me = this;
    console.log(this.options.url);
    $.get(this.options.url, params, function(result) {
      // inform about result
      me.options.onSuccess(result)
    }, me.options.format);
  }, 

});


