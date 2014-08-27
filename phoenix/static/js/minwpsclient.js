/*
 * A minimal WPS client implementation with only functionality required to add
 * the animation to the map.
 */

/*
 * Get the attribute with the given name from the DOM attributes list.
 */
function getAttribute(attributesContainingNode, attributeName){
    var attributes = attributesContainingNode.attributes;
    for (var i = attributes.length-1; i >=0 ; i--){
        if (attributes[i].nodeName === attributeName){
            var statusLocation = attributes[i].value;
            return statusLocation;
        }
    }
    return ""
}



function WpsClient(wpsUrl, wpsPort, proxyPort, myMap){
    this.wpsUrl = wpsUrl;
    this.wpsPort = wpsPort;
    this.proxyPort = proxyPort;
    this.timeout;
    this.myMap = myMap;
    this.delay = 2000;//time between request for WPS status in ms.
    this.addCounter = 0;//A pseudo lock to prevent adding more often than intended.
    _this = this;
    $("#animateGif").click(function(){
        _this.addGifAnimation();
        });
};

WpsClient.prototype.addGifAnimation = function(){
    var wmsUrls = this.myMap.getVisibleWMSLayersUrls();
    var startTime = $("#startframe").val();
    var endTime = $("#endframe").val();
    var frameDuration = parseFloat($("#period").val())/1000.0;
    var aggregation = $("#aggregation").val();
    var layerName = $("#wmsLayerName").val();
    var imageLayerName = $("#imageLayerName").val();
    this.addCounter++;
    this.addAnimation(wmsUrls, startTime, endTime, frameDuration, aggregation, layerName,
                           imageLayerName);
};

WpsClient.prototype.addAnimation = function(wmsUrls, startTime, endTime, frameDuration,
                                            aggregation, layerName, imageLayerName){
    var wmsUrlsString = wmsUrls[0];
    for (var i = 1; i < wmsUrls.length; i++){
        wmsUrlsString += ";wms_urls=" + wmsUrls[i];
    }
    wmsUrlsString += ";"
    var wpsurl = this.wpsUrl.split("?")[0]//use only the address and not the parameters
    var url = (wpsurl+"?request=execute&service=WPS&version=1.0.0"+
              "&identifier=WMS.GifAnimationMultiWMS" +
              "&datainputs=" + 
              "wms_urls=" + wmsUrlsString +
              ";start_time=" + startTime +
              ";end_time=" + endTime +
              ";frame_duration=" + frameDuration +
              ";aggregation=" + aggregation +
              ";layer_name=" + layerName
              );
    url += "&storeExecuteResponse=true&status=true"//ensure it runs async
    //find status location
    var statusLocationContainingXML = getURL(url);
    var statusLocation = this.getStatusLocation(statusLocationContainingXML);
    statusLocation = statusLocation.replace(":"+this.wpsPort, ":"+this.proxyPort);
    var finished = false;
    this.HandleProcessFinished(statusLocation, finished, imageLayerName);
}

/*
 * Get the statusLocation attribute from the root element from an XML repsonse text.
 */
WpsClient.prototype.getStatusLocation = function(xmlString){
    var xml = $.parseXML(xmlString);
    return getAttribute($(xml).children()[0], "statusLocation");
}

WpsClient.prototype.isProcessFinished = function(url,finished){
    var responseText = getURL(url);
    var hasException = (responseText.indexOf("<ows:ExceptionText>") > -1);
    if (hasException) {
        console.log("WPS process failed to generate a response. Check if all inputs are provided");
        this.addCounter--;
    }
    finished = (responseText.indexOf("<wps:ProcessSucceeded>") > -1);
    if(!finished && !hasException){
        this.showProcessStatus(responseText);
    }
    //If the process is finished fill the progress bar and let it disappear after a short delay.
    if (finished){
        this.setWpsProgressValue("100"); 
        setTimeout(function(){
            $("#AnimateProgress").css("display","none");
            },
            1000);
    }
    return finished;
}

WpsClient.prototype.setWpsProgressValue = function(percentCompleted){
    $("#WPSProgress").css("width", percentCompleted+"%").html(percentCompleted+"%");
    $("#AnimateProgress").css("display","block");
}

WpsClient.prototype.showProcessStatus = function(responseText){
    $xml = $($.parseXML(responseText));
    $progressElement = $xml.find("wps\\:ExecuteResponse wps\\:Status wps\\:ProcessStarted");
    var percentCompleted = getAttribute($progressElement[0], "percentCompleted");
    this.setWpsProgressValue(percentCompleted); 
};

WpsClient.prototype.getReference = function(processSucceededResponse, outputname){
    var xml = $.parseXML(processSucceededResponse);
    var reference;
    $xml = $(xml)
    $xml.children("wps\\:ExecuteResponse").children("wps\\:ProcessOutputs").children("wps\\:Output").each(
        function(){
            if ($(this).children("ows\\:Identifier")[0].textContent === outputname){
                reference = getAttribute($(this).children("wps\\:Reference")[0], "href");
            }
        });
    return reference;
}

/*
 * Request the status URL and check if the process is in a finished state.
 * TODO: The current implementation assumes that the process always succeeds.
 *
 * Due to JavaScript not offering a real sleep method the method simply 
 * uses branches and timeouts to emulate a sleep.
 */
WpsClient.prototype.HandleProcessFinished = function(url, finished, imageLayerName){
    if (this.addCounter >0){
        var _this = this;
        this.timeout = setTimeout(function(){finished = _this.isProcessFinished(url,finished)}, this.delay);
        if (finished) {
            this.addCounter--;
            clearTimeout(this.timeout);
            processSucceededResponse = getURL(url);
            imageref = this.getReference(processSucceededResponse, "animated_gif");
            this.myMap.addImage(imageLayerName, imageref);
        }
        else{
            setTimeout(function(){_this.HandleProcessFinished(url, finished, imageLayerName)}, this.delay);
        }
    }
    
}

