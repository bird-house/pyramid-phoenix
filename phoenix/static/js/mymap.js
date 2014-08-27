/********************
 * HELPER FUNCTIONS *
 ********************/

//method from http://stackoverflow.com/questions/133310/how-can-i-get-jquery-to-perform-a-synchronous-rather-than-asynchronous-ajax-re
function getURL(url){
    return $.ajax({
        type: "GET",
        url: url,
        cache: false,
        async: false
    }).responseText;
}

/*
 * Intersection method based on https://gist.github.com/jamiehs/3364281
 */
function intersection(a,b){
    return $.map(a, function(x){return $.inArray(x, b) < 0 ? null : x;});
}

/*
 * Add a getWeek method to Date using the ISO defintion of week.
 *
 * Taken from http://weeknumber.net/how-to/javascript
 * "License":
 * This script is released to the public domain and may be used, modified and
 * distributed without restrictions. Attribution not necessary but appreciated.
 * Source: http://weeknumber.net/how-to/javascript 
 */
Date.prototype.getWeek = function() {
  var date = new Date(this.getTime());
   date.setHours(0, 0, 0, 0);
  // Thursday in current week decides the year.
  date.setDate(date.getDate() + 3 - (date.getDay() + 6) % 7);
  // January 4 is always in week 1.
  var week1 = new Date(date.getFullYear(), 0, 4);
  // Adjust to Thursday in week 1 and count number of weeks from date to week1.
  return 1 + Math.round(((date.getTime() - week1.getTime()) / 86400000
                        - 3 + (week1.getDay() + 6) % 7) / 7);
};

/*
 * Storage class for an index and an array of time representing strings. 
 * Note: Used for live rendered animation in MyMap.
 */
function AnimationValues(startIndex, timeValues){
    this.index=startIndex;
    this.frames=timeValues;
}

/************************
 * MYMAP IMPLEMENTATION *
 ************************/
/*
 * MyMap creates a OpenLayers map object and adds basic features and a BaseLayer to it.
 *
 * Note: Overlay references to a non-base layer in Openlayers. This is used to avoid using 
 * NonBaseLayer or NBL in method names. Map layer is the layer on the OpenLayers map, while 
 * WMS layer is the layer in the WMS description.
 */
function MyMap(){
    var _this = this;
    var mapOptions = {eventListeners:{"changelayer": function(event){_this.updateOverlays()}}};
    var map = new OpenLayers.Map('map',mapOptions);
    this.map = map;
    this.map.addControl(new OpenLayers.Control.LayerSwitcher());
    //While map stores all Layers for the time update only the overlays are of interest. 
    //To prevent recalculating which ones are overlays every time they are stored in the overlays
    //variable.
    this.overlays = {};
    this.visibleOverlays = [];//used to store which overlays are visible.
    this.frameIndex=0;
    this.frameTimes = [];
    this.animationValues;
    this.addBaseLayers();
    this.addInteraction();
}

/*
 * Add the default BaseLayers to the map.
 *
 * Note: Currently there is no option to add further BaseLayers
 */
MyMap.prototype.addBaseLayers = function(){
    //Add the BaseLayer map
    this.addWMSBaseLayer("Worldmap OSGeo", "http://vmap0.tiles.osgeo.org/wms/vmap0?",
                         {layers: 'basic'}, {});
};

/*
 * Bind events to specific actions.
 */
MyMap.prototype.addInteraction = function(){
    var _this = this;
    $("#nextframeButton").click(function(){_this.nextFrame();});
    $("#startframeButton").click(function(){_this.startFrameFromIndex();});
    $("#endframeButton").click(function(){_this.endFrameFromIndex();});
    this.animationTimer;
    $("#animate").click(function(){_this.handleLiveAnimation();});
    $("#timeslider").on("input change", function(){_this.frameFromSlider();});
    //TODO: Tooltip for slider$("#timeslider").on("mousemove", function(event){ console.log(event);});
    $("#testbutton").click(function(){ _this.test();});
    $("#addwms").click(function(){ _this.addWMSFromForm();});
    $("#wmsurl").on("blur", function(){ _this.updateWMSForm();});
    $("#removewms").click(function(){ _this.removeSelectedMapLayer();});
}

MyMap.prototype.removeSelectedMapLayer = function(){
    var name = $("#removeMapLayerName").val();
    var _this = this;
    $layers = $(_this.map.layers);
    $layers.each(function(){
        if (this.name == name){
            _this.map.removeLayer(this);
        } 
    });
    this.updateAvailableMapLayers();
};

MyMap.prototype.updateWMSForm = function(){
    var url = $("#wmsurl").val();
    var names = this.getLayers(url)
    var text = "";
    for (var i = 0; i < names.length; i++){
        var name = names[i];
        if (["lon","lat"].indexOf(name) == -1){
            text+= '<option value="'+name+'">'+name+'</option>';
            }
        }
    $("#layer").html(text);
};
 
MyMap.prototype.addWMSFromForm = function(){
    //check if all important parameters are set
    var url = $("#wmsurl").val().split("?")[0];
    if (url === "")return;
    var layer = $("#layer").val();
    if (layer === null) return;
    //if the layer name is empty generate one
    if ($("#layername").val() == ""){
        $("#layername").val(this.suggestName(url));
        }
    var layername = $("#layername").val();
    if (this.isWMSOverlayNameUsed(layername)){
        alert("The name " + layername + " is aready in use.");
        return;
        }
    this.addWMSOverlay(layername, url, layer);
    this.updateAvailableMapLayers();
};

MyMap.prototype.updateAvailableMapLayers = function(){
    var removeableLayers = this.getWMSOverlayNames();
    var text="";
    $(removeableLayers).each(function(){
        var name = this.name;
        text+= '<option value="'+name+'">'+name+'</option>';
    });
    $("#removeMapLayerName").html(text);
};


/*
 * When the live rendered animation is not running the animation started and updates with the 
 * value set in period at the time of clicking the button. The button text changes to "Stop".
 *
 * If the animation is running the timer is cleared and the button is changed back to "Animate".
 */
MyMap.prototype.handleLiveAnimation = function(){
    if (this.animationTimer === undefined){
        this.startAnimation();
        var _this = this;
        this.animationTimer = setInterval(function(){_this.runAnimation();},
                                          parseInt($("#period").val()));
        $("#animate").val("Stop");
    }
    else{
        clearInterval(this.animationTimer);
        $("#animate").val("Animate");
    }
};
MyMap.prototype.getCapabilties = function(url){
    var urlhead = url.split("?")[0];
    var request = "?request=GetCapabilities&service=WMS&version=1.1.0"
    return getURL(urlhead+request);
    };
MyMap.prototype.getLayers = function(url){
    var text = this.getCapabilties(url);
    var xmlDoc = $.parseXML(text);
    var names =[];
    $xml = $(xmlDoc)
    $xml.find("Layer").children("Name").each(function(){
        names.push($(this).text())
        });
    return names;
    };

/*
 * The wms_url is used to get the capabilities. It is assumed that there is only one
 * entry matching to the Selector "Capability > Layer > Layer > Title" and that it has
 * a naming pattern similar to CORDEX. It will return the title up to and excluding the 
 * second "_". The length of the name is limited to 50 characters.
 *
 * @param {string} wms_url An url to a WMS server.
 */
MyMap.prototype.suggestName = function(wms_url){
    var capabilitiesXMLString = this.getCapabilties(wms_url);
    $xmlCaps = $($.parseXML(capabilitiesXMLString));
    var title = $xmlCaps.find("Capability>Layer>Layer>Title").text();
    var snp = title.split("_")
    var suggestedName;
    //If it follows CORDEX like notation use the first two facets.
    if (snp.length > 1) suggestedName= snp[0] + "_" + snp[1];
    //else use up to 50 characters of the title.
    else suggestedName = title.slice(0,50);
    return suggestedName;
    };
/*
 * Returs the names of the selectable WMS overlays.
 * Used for name colission, removal selection of WMS layers.
 */
MyMap.prototype.getWMSOverlayNames = function(){
    $layers = $(this.map.layers);
    var removeableLayers =[]
    $layers.each(function(){
        if ((this.isBaseLayer === false) && (this.CLASS_NAME==="OpenLayers.Layer.WMS")){
            removeableLayers.push(this);
            }
        });
    return removeableLayers;
    }

MyMap.prototype.isWMSOverlayNameUsed = function(layername){
    $layers = $(this.getWMSOverlayNames());
    layernames = [];
    $layers.each(function(){
        layernames.push(this.name);
    });
    return (layernames.indexOf(layername) >= 0);
};

////////MyMap.prototype.LayerFakeAnimation = function(){
////////    var steps = [ "2001-01-01T12:00:00.000Z",
////////                  "2001-01-02T12:00:00.000Z",
////////                  "2001-01-03T12:00:00.000Z",
////////                  "2001-01-04T12:00:00.000Z",
////////                  "2001-01-05T12:00:00.000Z",
////////                  "2001-01-06T12:00:00.000Z",
////////                  "2001-01-07T12:00:00.000Z",
////////                  "2001-01-08T12:00:00.000Z",
////////                  "2001-01-09T12:00:00.000Z",
////////                  "2001-01-10T12:00:00.000Z",
////////                  "2001-01-11T12:00:00.000Z",
////////                  "2001-01-12T12:00:00.000Z",
////////                  "2001-01-13T12:00:00.000Z",
////////                  "2001-01-14T12:00:00.000Z",
////////                  "2001-01-15T12:00:00.000Z",
////////                  "2001-01-16T12:00:00.000Z",
////////                  "2001-01-17T12:00:00.000Z",
////////                  "2001-01-18T12:00:00.000Z",
////////                  "2001-01-19T12:00:00.000Z",
////////                  "2001-01-20T12:00:00.000Z",
////////                  "2001-01-21T12:00:00.000Z",
////////                  "2001-01-22T12:00:00.000Z",
////////                  "2001-01-23T12:00:00.000Z",
////////                  "2001-01-24T12:00:00.000Z",
////////                  "2001-01-25T12:00:00.000Z",
////////                  "2001-01-26T12:00:00.000Z",
////////                  "2001-01-27T12:00:00.000Z",
////////                  "2001-01-28T12:00:00.000Z",
////////                  "2001-01-29T12:00:00.000Z",
////////                  "2001-01-30T12:00:00.000Z",
////////                  "2001-01-31T12:00:00.000Z",
////////                  ]
////////    var name = "EUR-44-tasmax"
////////    var url = "http://localhost:12345/thredds/wms/test/tasmax_EUR-44_IPSL-IPSL-CM5A-MR_historical_r1i1p1_SMHI-RCA4_v1_day_20010101-20051231.nc";
////////    var layername = "tasmax";
////////    var timeLayers = {};//map layername to a list of layers
////////    for (var i = 0; i < steps.length; i++){timeLayers[steps[i]] = []}
////////    //Create the Layers
////////    for (var i = 0; i < steps.length; i++){
////////        var time = steps[i];
////////        var layer = new OpenLayers.Layer.WMS(name, url, {LAYERS:layername, transparent: true,
////////                                             time:time}, {singleTile:true, isBaseLayer:false});
////////        this.map.addLayer(layer);
////////        layer.setVisibility(true);
////////        timeLayers[time].push(layer); 
////////        }
////////    //Turn all layers invisible
////////    for (var i = 0; i < steps.length; i++){
////////        var layers = timeLayers[steps[i]];
////////        for (var j=0; j < layers.length; j++){
////////            layers[j].setVisibility(false);
////////            }
////////        }
////////    //Initialize animation
////////    var currentIndex = 0;
////////    startLayers = timeLayers[steps[0]];
////////    for (var i = 0; i < startLayers.length; i++){
////////        startLayers[i].setVisibility(true);
////////        }
////////    //Define the method to run on timeout
////////    function nextFrame(){
////////        var oldLayers = timeLayers[steps[currentIndex]]
////////        currentIndex++;
////////        if(currentIndex >= steps.length){currentIndex = 0;}
////////        var newLayers = timeLayers[steps[currentIndex]];
////////        for (var i=0; i < newLayers.length; i++){
////////            newLayers[i].setVisibility(true);
////////            }
////////        for (var i=0; i < oldLayers.length; i++){
////////            oldLayers[i].setVisibility(false);
////////            }
////////        this.fakeAnimation = setTimeout(nextFrame, parseInt($("#period").val()))
////////        }
////////    
////////    this.fakeAnimation = setTimeout(nextFrame, 1000);
////////};

MyMap.prototype.startAnimation = function(){
    start = $("#startframe").val();
    end = $("#endframe").val();
    aggregation = $("#aggregation").val();
    var times = this.filterTimesteps(this.frameTimes, aggregation, start, end);
    this.animationValues = new AnimationValues(0,times);
};

MyMap.prototype.runAnimation = function(){
    var i = this.animationValues.index;
    var time = this.animationValues.frames[i];
    //update the silder. This will cause the event "input change" for #timeslider
    var j = this.frameTimes.indexOf(time);
    $("#timeslider").val(j);
    //show the new frame
    this.showTimeFrame(time);
    //circle through the animation frames
    i++;
    if (i >= this.animationValues.frames.length) i = 0;
    this.animationValues.index = i;
};

//////MyMap.prototype.startGifAnimation = function(){
//////    start = $("#startframevalue").html();
//////    end = $("#endframevalue").html();
//////    aggregation = $("#aggregation").val();
//////    var times = this.filterTimesteps(this.frameTimes, aggregation, start, end);
//////    var limitFrames = $("#maxframes").val();
//////    times = times.slice(0,limitFrames);
//////    var time = times.join(",");
//////    for (var i = 0; i < this.visibleOverlays.length; i++){
//////        var overlay = this.visibleOverlays[i];
//////        //var animatedurl = overlay.url+"?"
//////        //animatedurl += "TIME="+time;
//////        //animatedurl += "&TRANSPARENT=true";
//////        //animatedurl += "&FORMAT=image/gif";
//////        overlay.mergeNewParams({'time':time, format:"image/gif"});
//////    }
//////};


/*
 * Updates the information about timesteps and visible overlays. Should be run on each
 * change of selected Overlays. 
 */
MyMap.prototype.updateOverlays = function(){
    this.visibleOverlays = [];
    for (name in this.overlays){
        var overlay = this.overlays[name];
        if(overlay.visibility){
            this.visibleOverlays.push(overlay);
        }
    }
    if (this.visibleOverlays.length > 0){
        this.frameTimes = this.visibleOverlays[0].timesteps;
        for (var i=1; i < this.visibleOverlays.length; i++){
            this.frameTimes = intersection(this.frameTimes, this.visibleOverlays[i].timesteps);
        }
    }
    else{//no visible frames => no timesteps to select from
        this.frameTimes = [];
    }
    //update the sliders maximum value
    $("#timeslider").attr('max', this.frameTimes.length);
};

/*
 * Show the next frame in the complete list of available timeframes
 * in all visible overlays.
 */
MyMap.prototype.nextFrame = function(){
    this.frameIndex+=1;
    $("#timeslider").val(this.frameIndex);
    $("#timeslider").attr("max",this.frameTimes.length);
    this.showFrame();
};

/*
 * Select a frame from the complete list of available timeframes
 * in all visible overlays.
 */
MyMap.prototype.frameFromSlider = function(){
    this.frameIndex = parseInt($("#timeslider").val());
    this.showFrame();
};

/*
 * Find the time value for the currently selected frame and 
 * request to update the visible layers with this time.
 */
MyMap.prototype.showFrame = function(){
    if (this.frameIndex >= this.frameTimes.length){this.frameIndex = 0;}
    if (this.frameTimes.length != 0){
        var time = this.frameTimes[this.frameIndex];
        this.showTimeFrame(time);
    }
};

/*
 * Update the visible layers to show the provided time. 
 * 
 * Note: Does not prevent using invalid time values. 
 */
MyMap.prototype.showTimeFrame = function(time){
    $("#currentDateTime").html(time);
    for (var i=0; i < this.visibleOverlays.length; i++){
        overlay = this.visibleOverlays[i];
        overlay.mergeNewParams({'time':time});
    }
};

/*
 * Sets the value of the start time input element to the currently indexed time.
 */
MyMap.prototype.startFrameFromIndex = function(){
    $("#startframe").val(this.frameTimes[this.frameIndex]);
};

/*
 * Sets the value of the end time input element to the currently indexed time.
 */
MyMap.prototype.endFrameFromIndex = function(){
    $("#endframe").val(this.frameTimes[this.frameIndex]);
};

/*
 * Add a BaseLayer to the map. Only one BaseLayer can be active at a time (selected with radiobox).
 * @param {string} name Name of the BaseLayer in the GUI (e.g. EUR-44-tasmax)
 * @param {string} url The WMS url
 * @param {json} params The OpenLayers params (e.g. {layers:"basic"})
 * @param {json} options The OpenLayers options.
 */
MyMap.prototype.addWMSBaseLayer = function(name, url, params, options){
    wmsLayer = new OpenLayers.Layer.WMS(name, url, params, options);
    wmsLayer.isBaseLayer = true;
    //wmsLayer.wrapDateLine= true;
    this.map.addLayer(wmsLayer);};

/*
 * Add an Overlay that contains timesteps. 
 * For now the timesteps will be extracted from the WMS file using an external process.
 * @param {string} name The name of the layer in the select list (e.g. EUR-44-tasmax)
 * @param {string} url The url to the WMS with the specific file. (e.g copy WMS line from THREDDS)
 * @param {string} layerName the name of Layer (e.g. tasmax)
 * @param {json} options For details see OpenLayers documentation. (Default = {}) 
 */

MyMap.prototype.addWMSOverlay = function(name, url, layerName, options){
    if (options === undefined){
        options = {singleTile:true};};
    params = {layers: layerName, transparent:true};
    wmsLayer = new OpenLayers.Layer.WMS(name, url, params, options);
    wmsLayer.isBaseLayer = false;
    this.addTimesteps(wmsLayer);
    this.overlays[name] = wmsLayer;
    this.map.addLayer(wmsLayer);
    };


/*
 * Get capabilities, add the timesteps property to the overlay and then update the overlays.
 * @param {OpenLayers.Layer} overlay The Layer object which will have the timesteps property added.
 */
MyMap.prototype.addTimesteps = function(overlay){
    //Extract needed variables from the Layer overlay.
    var wmsurl = overlay.url;
    var layerName = overlay.params.LAYERS;
    var version = overlay.params.VERSION;
    //Prepare for the request
    var wmsFormat = new OpenLayers.Format.WMSCapabilities({version: version});
    var _this = this;
    OpenLayers.Request.GET({
        url: wmsurl,
        params:{
            SERVICE: 'WMS',
            VERSION: version,
            REQUEST: 'GetCapabilities'},
        success: function(response){
            var wmsCaps = wmsFormat.read(response.responseText);
            var layers = wmsCaps.capability.layers;
            var layer;
            for (var i=0; i < layers.length; i++){
                if (layers[i].name === layerName){
                    layer = layers[i];
                    break;}}
            if (layer != undefined) {
                var timesteps = layer.dimensions.time.values;
                //The first timestep might look like "\n              2001-..."
                //and should be like "2001-..."
                timesteps[0]=timesteps[0].replace(/\n| /g,"");
                overlay.timesteps = timesteps;
                //now that the values for timesteps are set the overlay information has to be 
                //updated.
                _this.updateOverlays()
                }}});

};

/*
 * Filter a given timesteps array to contain only timesteps matching to the 
 * aggregation from start to end.
 *
 * @param {Date compatible Array} timesteps An array of values that can be parsed by Date. 
 * @param {string} aggregation The step size selectable from ["daily", "weekly", "monthly", "yearly"] 
 * @param {Date compatible} start The start time. Any timestep before it is ignored.
 * @param {Date compatible} end The end time. Any timestep after it is ignored.
 * @param {boolean} sort Set to true if the timesteps are not sorted.
 */

MyMap.prototype.filterTimesteps = function(timesteps, aggregation, start, end, sort){
    var validAggregations = ["daily", "weekly", "monthly", "yearly"];
    if (validAggregations.indexOf(aggregation) === -1 ){
        throw ("Aggregation "+aggregation+" is not in "+validAggregations.join(", "));}
    startDate = new Date(start);
    endDate = new Date(end);

    //sort the data
    if (sort === undefined) sort = false;
    var sortedTimesteps;
    var filteredTimesteps = [];
    var lastAddedDate;
    if (sort) sortedTimesteps = timesteps.sort();
    else sortedTimesteps = timesteps;
    //find the starting index
    var j;
    for (var i=0; i < sortedTimesteps.length; i++){
        var currentDate = new Date(sortedTimesteps[i]);
        //as long as it is before start date get the next Date
        if (currentDate < startDate) continue;
        lastAddedDate = currentDate;
        j = i;
        break;}
    //Add the first element to the list
    filteredTimesteps.push(sortedTimesteps[j]);
    //Search the rest of dates for matching according to aggregation.
    for (var i =j+1; i < sortedTimesteps.length; i++){
        var currentDate = new Date(sortedTimesteps[i]);
        //if it is past the end date stop looking for further timesteps.
        if (currentDate > endDate) break;
        //The current date is now between start and end date
        if (aggregation == "daily"){
            if (currentDate.getDate() == lastAddedDate.getDate()) continue;}
        else if (aggregation == "weekly"){
            if (currentDate.getWeek() == lastAddedDate.getWeek()) continue;}
        else if (aggregation == "monthly"){
            if (currentDate.getMonth() == lastAddedDate.getMonth()) continue;}
        else if (aggregation == "yearly"){
            if (currentDate.getYear() == lastAddedDate.getYear()) continue;}
        lastAddedDate = currentDate;
        filteredTimesteps.push(sortedTimesteps[i]);
        }
    return filteredTimesteps;

};

MyMap.prototype.addImage = function(name, imageref){
    imageLayer = new OpenLayers.Layer.Image(
        name,
        imageref,
        new OpenLayers.Bounds(-180, -90, 180, 90),
        new OpenLayers.Size(50,50),//chosen such that at any zoom the overlay is visible.
        {numZoomLevels: 12, isBaseLayer: false}
    );
    
    this.map.addLayer(imageLayer);
}

/*
 * Returns the visible WMS layers urls as list.
 */
MyMap.prototype.getVisibleWMSLayersUrls = function(){
    $layers = $(this.map.layers);
    var visibleLayers =[]
    $layers.each(function(){
        if ((this.isBaseLayer === false) && (this.CLASS_NAME==="OpenLayers.Layer.WMS")){
            visibleLayers.push(this.url);
            }
        });
    return visibleLayers;
    
}

/*
 * Build in self test will run some tests.
 * They can later be transferred to a real unittest/itegrationtest.
 */
MyMap.prototype.bist = function(){
    var testsOkay = 0;
    var testsFail = 0;
    function test(condition, errormessage){
        if(condition) testsOkay++;
        else{
            testsFail++;
            console.log(errormessage);}};
    //quick and dirty equal for arrays of basic types
    function arrayEqual(a1,a2){
        if (a1.length == a2.length){
            for (var i = 0; i < a1.length; i++){
                if(a1[i] !== a2[i]) return false;}}
        else return false;
        return true;};
     
    //test arrayEqual
    function testArrayEqual(x,y){test(arrayEqual(x,y), 
                             ("Error in arrayEqual: " + x + " and " + y + " should be equal"))};
    function testArrayNotEqual(x,y){test(!arrayEqual(x,y), 
                             ("Error in arrayEqual: " + x + " and " + y + " should not be equal"))};
    var a = [1,2];
    var b = [2,3];
    var c = [1,2];
    var d = [1,2,3];
    var e = [1,"2"];
    testArrayNotEqual(a,b);
    testArrayEqual(a,c);
    testArrayNotEqual(a,d);
    testArrayNotEqual(a,e);
    //Test filter_timesteps
    function testFilterTimesteps(filteredTimesteps, assumedFT){
             if(arrayEqual(filteredTimesteps, assumedFT)) testsOkay++;
             else{
                 testsFail++;
                 console.log("Error: MyMap.prototype.filter_timesteps returned "+
                             "[" + filteredTimesteps.join(", ") + "]" +
                             " instead of [" + assumedFT.join(", ") + "]");}};
    var timesteps = ["2001-01-01T12:00:00.000Z", "2001-01-03T12:00:00.000Z","2001-01-05T12:00:00.000Z"];
    //start and end do not match with a timestep
    var filteredTimesteps = this.filterTimesteps(timesteps, "daily", "2001-01-02", "2001-01-04");
    var assumedFT = [timesteps[1]];
    testFilterTimesteps(filteredTimesteps, assumedFT);
    //start is before the first timestep and end is before the last timestep but at the same day.
    //the last element should not be part of the filterd items.
    var filteredTimesteps2 = this.filterTimesteps(timesteps, "daily", "2001-01-01", "2001-01-05")
    var assumedFT2 = [timesteps[0], timesteps[1]];
    testFilterTimesteps(filteredTimesteps2, assumedFT2);
    //test weekly (week 1,2,2,4,4,4)
    var timestepsW = ["2001-01-01T12:00:00.000Z", "2001-01-13T12:00:00.000Z",
                      "2001-01-14T12:00:00.000Z", "2001-01-22T12:00:00.000Z",
                      "2001-01-23T12:00:00.000Z", "2001-01-24T12:00:00.000Z"];
    var filteredTimestepsW = this.filterTimesteps(timestepsW, "weekly", "2001-01-01", "2001-08-05")
    var assumedFTW = [timestepsW[0], timestepsW[1], timestepsW[3]];
    testFilterTimesteps(filteredTimestepsW, assumedFTW);
    //test monthly 
    var timestepsM = ["2001-01-01T12:00:00.000Z", "2001-02-13T12:00:00.000Z",
                      "2001-02-14T12:00:00.000Z", "2001-06-22T12:00:00.000Z",
                      "2001-06-23T12:00:00.000Z", "2001-11-24T12:00:00.000Z"];
    var filteredTimestepsM = this.filterTimesteps(timestepsM, "monthly", "2001-01-01", "2001-08-05")
    var assumedFTM = [timestepsM[0], timestepsM[1], timestepsM[3]];//timestepsM[5] is after end
    testFilterTimesteps(filteredTimestepsM, assumedFTM);
    //test yearly 
    var timestepsY = ["2001-01-01T12:00:00.000Z", "2001-02-13T12:00:00.000Z",
                      "2002-02-14T12:00:00.000Z", "2002-06-22T12:00:00.000Z",
                      "2006-06-23T12:00:00.000Z", "2007-11-24T12:00:00.000Z"];
    var filteredTimestepsY = this.filterTimesteps(timestepsY, "yearly", "2001-01-01", "2011-08-05")
    var assumedFTY = [timestepsY[0], timestepsY[2], timestepsY[4], timestepsY[5]];
    testFilterTimesteps(filteredTimestepsY, assumedFTY);

    function testEqual(a, b){
             if(a === b) testsOkay++;
             else{
                 testsFail++;
                 console.log(a + " is not equal to " + b);
                 }
             };



    //Summary of all tests
    console.log("=================================================");
    console.log("PASSED: " + testsOkay);
    console.log("FAILED: " + testsFail);
};

