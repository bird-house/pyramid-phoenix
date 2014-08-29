/*
 * Author: Tobias Kipp (kipp@dkrz.de)
 */

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
    this.timeLabel = this.addTimeLabel(-150,-80, "Time", "", 12);
}

/*
 * Adds The legend graphic to its reserved slot. The color scale range is 
 * taken from the page. 
 *
 * If the pages values for minimum and maximum are not numbers the method will
 * do nothing. 
 *
 * @param {OpenLayers.Layer.WMS} layer The layer to extract the legend from.
 * @param {string} style A style that can be found in the WMS capabilities. (e.g. boxfill/rainbow)
 * @param {int} width The width of the legend graphic.
 * @param {int] height The height of the legend graphic.
 */
MyMap.prototype.addLegendGraphic = function(layer, style, width, height){
    var colorscalerange = this.getMinMaxColorscalerangeString();
    if (colorscalerange === undefined) {return}
    var numColorBands = "50";
    var legendUrl = (layer.url + "?REQUEST=GetLegendGraphic&COLORBARONLY=true" + 
                     "&WIDTH=" + width + "&HEIGHT=" + height + "&PALETTE=" + style +
                     "&NUMCOLORBANDS=" + numColorBands +
                     "&COLORSCALERANGE="+ colorscalerange);
    $("#legendimg")[0].src = legendUrl;

};

MyMap.prototype.addTimeLabel = function(x, y, title, text, fontsize){
    var vectorLayer = new OpenLayers.Layer.Vector(title, 
    {
        styleMap: new OpenLayers.StyleMap(            
        {
            label : "${labelText}",                    
            fontColor: "blue",
            fontSize: fontsize+"px",
            fontFamily: "Courier New, monospace",
            fontWeight: "bold",
            labelAlign: "lc",
            labelXOffset: "14",
            labelYOffset: "0",
            labelOutlineColor: "white",
            labelOutlineWidth: 3
        })
    });
    var features = [];
    var pt =  new OpenLayers.Geometry.Point(x,y);
    features.push(new OpenLayers.Feature.Vector(pt, {labelText:text}));
    vectorLayer.addFeatures(features);
    this.map.addLayer(vectorLayer);
    return vectorLayer;
};

MyMap.prototype.setTimeLabelText = function(text){
    var extent = this.map.getExtent();
    var feature = this.timeLabel.features[0];
    var dx = extent.left-feature.geometry.x;
    var dy = extent.bottom-feature.geometry.y;
    feature.geometry.move(dx,dy+6);
    //feature.geometry.move(0,0);
    feature.attributes.labelText=text;
    this.timeLabel.redraw();
};
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
    $("#nextFrameButton").click(function(){_this.nextFrame();});
    $("#prevFrameButton").click(function(){_this.prevFrame();});
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
    $("#mincol").on("blur", function(){_this.applyColorScale()});
    $("#maxcol").on("blur", function(){_this.applyColorScale()});
}

MyMap.prototype.getMinMaxColorscalerangeString = function(){
    var min = parseFloat($("#mincol").val());
    var max = parseFloat($("#maxcol").val());
    if (isNaN(min) || isNaN(max)){
        return undefined;
    }
    var direction = 1;
    if (max < min){
        var min_old = min;
        min = max;
        max = min_old;
        $("#legendimg").addClass("mirrorimage");
        direction = -1;
    }
    else{
        $("#legendimg").removeClass("mirrorimage");
    }
    this.updateLegendColorValue(min, max, direction);
    return  min + "," + max;
}
/*
 * The map color values are for 10, 30, 50, 70 and 90 percent and dependent on the 
 * direction they are up-down or down-up. The ids of the elements are px0col with x being
 * the most significant digit.
 * If the direction is -1 the identifiers are generated in inverse order to the value to fix the 
 * naming issue.
 */
MyMap.prototype.updateLegendColorValue = function(min, max, direction){
    var start = -50*(direction-1)
    var cur = start + direction * 10; 
    var dyPercent = (max-min)/100; //To calcuate the percentage only once it is added here.
    for (var i = 0; i < 5; i++)
    {
        var id = "#p"+ (start + cur * direction )+"col";
        var val = cur * dyPercent + min;
        $(id).html(val);
        cur = cur + direction * 20;
    }
};

/*
 * Applies the colorscalerange to all WMS layers. 
 * It will do nothing if the colorscalerange can not be correctly generated from the pages values.
 */
MyMap.prototype.applyColorScale = function(){
    
   var colorscalerange = this.getMinMaxColorscalerangeString();
   if (colorscalerange === undefined){return}
   var layers = this.map.layers;
   for (var i = 0; i < layers.length; i++){
       var layer = layers[i];
       if (layer.CLASS_NAME == "OpenLayers.Layer.WMS"){
           layer.mergeNewParams({"colorscalerange": colorscalerange});
           this.addLegendGraphic(layer, "boxfill/rainbow", 50, 500);//see map.css for height
       }
   }
};
/*
 * Adding a WMS layer to the map will add a wmslayername property to the OpenLayers layer,
 * which will be read here to update the list of selectable layers in the Animate tab.
 */
MyMap.prototype.updateActiveWMSLayerNames = function(){
    var layers = this.map.layers;
    var activeWmsLayersHtml = ""
    for (var i=0; i <layers.length; i++){
        if (layers[i].visibility === true){
            var wmsLayerName = layers[i].wmslayername;
            if(wmsLayerName !== undefined){
                activeWmsLayersHtml += '<option value="' + wmsLayerName + '">' + wmsLayerName + '</option>';
            }
        }
    }
    $("#wmsLayerName").html(activeWmsLayersHtml)
};

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
    if ($("#title").val() == ""){
        $("#title").val(this.suggestName(url));
        }
    var title = $("#title").val();
    if (this.isWMSOverlayNameUsed(title)){
        alert("The name " + title + " is aready in use.");
        return;
        }
    this.addWMSOverlay(title, url, layer);
    this.updateAvailableMapLayers();
};

MyMap.prototype.updateAvailableMapLayers = function(){
    var removeableLayers = this.getWMSOverlayNames();
    var removeableNames="";
    $(removeableLayers).each(function(){
        var name = this.name;
        removeableNames+= '<option value="'+name+'">'+name+'</option>';
    });
    $("#removeMapLayerName").html(removeableNames);
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
        $("#animate").html("Stop (live)");
    }
    else{
        clearInterval(this.animationTimer);
        $("#animate").html("Animate (live)");
        this.animationTimer=undefined;
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
    this.updateActiveWMSLayerNames();
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

MyMap.prototype.prevFrame = function(){
    this.frameIndex-=1;
    if(this.frameIndex < 0){this.frameIndex = this.frameTimes.length-1;}
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
    this.setTimeLabelText(time);
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
 * @param {string} title The title of the OpenLayers layer (e.g. EUR-44-tasmax)
 * @param {string} url The url to the WMS with the specific file. (e.g copy WMS line from THREDDS)
 * @param {string} layerName the name of Layer (e.g. tasmax)
 * @param {json} options For details see OpenLayers documentation. (Default = {}) 
 */

MyMap.prototype.addWMSOverlay = function(title, url, layerName, options){
    if (options === undefined){
        options = {singleTile:true};};
    params = {layers: layerName, transparent:true};
    wmsLayer = new OpenLayers.Layer.WMS(title, url, params, options);
    wmsLayer.isBaseLayer = false;
    wmsLayer.wmslayername=layerName;
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

