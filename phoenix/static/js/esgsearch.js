var wps;

function esgsearch() {

  // set the proxy
  //OpenLayers.ProxyHost = "/cgi-bin/proxy.cgi?url=";
                
  // set the url
  var url = "http://tracy.local:8090/wps";

  // init the client
  wps = new OpenLayers.WPS(url,{
    onDescribedProcess: onDescribeProcess,
    onSucceeded: onExecuted
  });

  // run Execute
  wps.describeProcess("de.dkrz.esgf.search");
};

/**
 * DescribeProcess
 */
function onDescribeProcess(process) {
  process.inputs[0].setValue('');
  
  wps.execute("dummyprocess");
};

/**
 * This function is called, when DescribeProcess response
 * arrived and was parsed
 */
function onExecuted(process) {
  var executed = "<h3>"+process.title+"</h3>";
  executed += "<h3>Abstract</h3>"+process.abstract;

  executed += "<h3>Outputs</h3><dl>";

  // for each output
  for (var i = 0; i < process.outputs.length; i++) {
    var output = process.outputs[i];
    executed += "<dt>"+output.identifier+"</dt>";
    executed += "<dd>Title: <strong>"+output.title+"</strong><br />"+
      "Abstract: "+output.abstract+"</dd>";
    executed += "<dd>"+"<strong>Value:</strong> "+
      output.getValue()+"</dd>";
  }
  executed += "</dl>";
  document.getElementById("wps-result").innerHTML = executed;

};
