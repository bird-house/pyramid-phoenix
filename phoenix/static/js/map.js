var map = null;
var wmsLayer = null;
var animateLayer = null;
var animateURL = null;
var start_time, end_time;
var layerList;
var selectedLayer = null;
var selectedTimeIndex = null;
var layersLoading = 0;
var opacity = 0.7;
var layerSwitcher = null;

function initMap(openid) {
  //var mapOptions = { maxResolution: 256/512, numZoomLevels: 11, fractionalZoom: true};
  //map = new OpenLayers.Map('map',mapOptions);
  map = new OpenLayers.Map('map', { controls: [] });
  layerSwitcher = new OpenLayers.Control.LayerSwitcher()
  map.addControl(layerSwitcher);
  map.addControl(new OpenLayers.Control.Navigation());
  map.addControl(new OpenLayers.Control.PanZoom());
  //map.addControl(new OpenLayers.Control.Attribution());

  // Set up the throbber (acts as progress indicator)
  // Adapted from LoadingPanel.js
  map.events.register('preaddlayer', map, function(evt) {
    if (evt.layer) {
      evt.layer.events.register('loadstart', this, function() {
        loadStarted();
      });
      evt.layer.events.register('loadend', this, function() {
        loadFinished();
      });
    }
  });

  // base layer
  var baseLayer = null;

  baseLayer = new OpenLayers.Layer.WMS( 
    "Demis BlueMarble",
    "http://www2.demis.nl/wms/wms.ashx?WMS=BlueMarble" , 
    {layers: 'Earth Image,Borders,Coastlines'});
  map.addLayer(baseLayer);

  /*
  baseLayer = new OpenLayers.Layer.WMS( 
    "OpenLayers WMS",
    "http://labs.metacarta.com/wms-c/Basic.py?", {layers: 'basic'});
  addLayer(baseLayer);
  */
  
  baseLayer = new OpenLayers.Layer.WMS( 
    "Demis WMS",
    "http://www2.demis.nl/wms/wms.ashx?WMS=WorldMap",
    {layers:'Countries,Bathymetry,Topography,Hillshading,Coastlines,Builtup+areas,Waterbodies,Rivers,Streams,Railroads,Highways,Roads,Trails,Borders,Cities,Airports',
     format: 'image/png'});
  map.addLayer(baseLayer);
 
  map.zoomToMaxExtent();

  // more controls
  initOpacitySlider();
  initLayerList(openid);
}

function loadStarted() {
  layersLoading++;
  if (layersLoading > 0) {
    $('#loading-indicator').show();
  }
}

function loadFinished() {
  if (layersLoading > 0) {
    layersLoading--;
  }
  if (layersLoading == 0) {
    $('#loading-indicator').hide();
  }
}

function initOpacitySlider() {
  $("#opacity-slider").slider({
    value: opacity,
    min: 0.1,
    max: 1.0,
    step: 0.1,
    slide: function(e, ui) {
      //console.log("sliding ...");
      setOpacity(ui.value, false);
    },
    change: function(e, ui) {
      //console.log("sliding ...");
      setOpacity(ui.value, true);
    }
  });
  setOpacity(opacity, false);
}

function setOpacity(newOpacity, redraw) {
  opacity = newOpacity;
  if (wmsLayer != null) {
    console.log("update layer");
    wmsLayer.setOpacity(opacity);
    if (redraw) wmsLayer.redraw();
  }
  if (animateLayer != null) {
    animateLayer.setOpacity(opacity);
    if (redraw) animateLayer.redraw();
  }

  $("#opacity-label").text("Overlay Opacity " + opacity*100 + "%");
}

function initLayerList(openid) {
  wps = new SimpleWPS({
    process: "org.malleefowl.wms.layer",
    onSuccess: function(result) {
      //console.log(result);
      var output = [];
      layerList = []
      $.each(result, function(index, layer) {
        //output.push('<optgroup label="' + layer.service_name + '">');
        title = layer.title + " (" + layer.service_name + ")";
        output.push('<option label="' + title + '" value="'+ index +'">' + title +'</option>'); 
        //output.push('</optgroup>');
        layerList.push(layer);
      });
      $('#select').html(output.join(''));

      $('#select').change(function() {
        selectedLayer = layerList[this.selectedIndex];
        showWMSLayer(selectedLayer);
      });

      if (layerList.length > 0) {
        selectedLayer = layerList[0];
        showWMSLayer(selectedLayer);
      }
    },
  });
  wps.execute({
    openid: openid,
  });
}

function showWMSLayer(layer) {
  if (wmsLayer != null) {
    //console.log("remove wms layer");
    map.removeLayer(wmsLayer);
    wmsLayer = null;
  }
  initWMSLayer(layer, 0);
  initTimeSlider(layer);
}

function initWMSLayer(layer, step) {
  console.log("init wms layer: title=" + layer.name + ", time=" + layer.timesteps[step])

  wmsLayer = new OpenLayers.Layer.WMS(
    layer.title,
    layer.service,
    {
      layers: layer.name,
      transparent: 'true',
      format:'image/png',
      time: layer.timesteps[step],
    },
    {
      isBaseLayer: false,
      opacity: opacity,
    });
  map.addLayer(wmsLayer);
}

function initTimeSlider(layer) {
  var max = layer.timesteps.length - 1;

  // slider
  $("#slider").slider({
    value: 0,
    min: 0,
    max: max,
    step: 1,
    slide: function(e, ui) {
      var step = parseInt(ui.value);
      //console.log("sliding ...");
      $("#time").text(dateLabel(layer.timesteps[step]));
    },
    change: function(e, ui) {
      var step = parseInt(ui.value);
      //console.log("step: " + step);
      $("#time").text(dateLabel(layer.timesteps[step]));
      wmsLayer.mergeNewParams({'time': layer.timesteps[step]});
      selectedTimeIndex = step;
    }
  });
  $("#time").text(dateLabel(layer.timesteps[0]));
  wmsLayer.mergeNewParams({'time': layer.timesteps[0]});
  selectedTimeIndex = 0;

  // prev button
  $("#prev").button({
    text: false,
  }).click(function( event ) {
    //console.log('prev button clicked');
    current = $("#slider").slider( "values", 0 );
    if (current > 0 ) {
      $("#slider").slider( "value", current - 1 );
    }
  });

  // next button
  $("#next").button({
    text: false,
  }).click(function( event ) {
    //console.log('next button clicked');
    current = $("#slider").slider( "values", 0 );
    if (current < max ) {
      $("#slider").slider( "value", current + 1 );
    }
  });

  // play button
  $("#play").button({
    text: false,
  }).click(function( event ) {
    if (animateLayer != null) {
      animateLayer.setVisibility(true);
    }
    else {
      $("#dialog-play").dialog({
        resizable: false,
        height: 300,
        modal: true,
        buttons: {
          Ok: function() {
            $( this ).dialog( "close" );
            animate(selectedLayer);
          },
          Cancel: function() {
            $( this ).dialog( "close" );
          }
        }
      });
    }
  });

  // stop button
  $("#pause").button({
    text: false,
  }).click(function( event ) {
    if (animateLayer != null) {
      animateLayer.setVisibility(false);
    }
  });
  
  // stop button
  $("#stop").button({
    text: false,
  }).click(function( event ) {
    if (animateLayer != null) {
      map.removeLayer(animateLayer);
      animateLayer = null;
    }
  });

  // googleearth button
  $("#googleearth").button({
    text: false,
  }).click(function( event ) {
      $("#dialog-play").dialog({
        title: 'Run Animation on GoogleEarth?',
        resizable: false,
        height: 250,
        modal: true,
        buttons: {
          Ok: function() {
            $( this ).dialog( "close" );
            animateOnGoogleEarth(selectedLayer);
          },
          Cancel: function() {
            $( this ).dialog( "close" );
          }
        }
      });
  });

  // slider range
  $("#slider-range").slider({
    range: true,
    values: [0, max],
    min: 0,
    max: max,
    step: 1,
    slide: function(e, ui) {
      var step0 = parseInt(ui.values[0]);
      var step1 = parseInt(ui.values[1]);
      
      setTimeRange(layer, step0, step1);
    },
  });

  setTimeRange(layer, 0, layer.timesteps.length-1);
}

function setTimeRange(layer, min, max) {
  $("#time-range").text( dateLabel(layer.timesteps[min]) + " - " + dateLabel(layer.timesteps[max]) );
  start_time = layer.timesteps[min];
  end_time = layer.timesteps[max];
} 

function setVisibility(animate) {
  console.log("set visibility: " + animate);
  if (wmsLayer != null) {
    wmsLayer.setVisibility(true);
    wmsLayer.displayInLayerSwitcher = false;
  }
  setLayerVisibility(animateLayer, animate);

  layerSwitcher.layerStates = []; // forces redraw
  layerSwitcher.redraw();
}

function setLayerVisibility(layer, visible) {
  if (layer != null) {
    layer.setVisibility(visible);
    layer.displayInLayerSwitcher = visible;
  }
}

function dateLabel(timestep) {
  return timestep.substring(0,16);
}

function initAnimateLayer(layer, timesteps) {
  animateLayer = new OpenLayers.Layer.WMS(
    "Animation",
    layer.service,
    {
      layers: layer.name,
      transparent: 'true',
      format:'image/gif',
      time: timesteps,
    },
    {
      singleTile: true, 
      ratio: 1,
      isBaseLayer: false,
      opacity: opacity,
    });
  map.addLayer(animateLayer);
}

function animate(layer) {
  if (animateLayer != null) {
    map.removeLayer(animateLayer);
    animateLayer = null;
  }

  loadStarted();
  wps = new SimpleWPS({
    process: "org.malleefowl.wms.animate.timesteps",
    onSuccess: function(timesteps) {
      //console.log(result);
      initAnimateLayer(layer, timesteps);
      loadFinished();
    },
  });
  wps.execute({
    service_url: layer.service,
    layer: layer.name,
    start: start_time,
    end: end_time,
    resolution: $("#select-resolution").val(),
  });
}

function animateOnGoogleEarth(layer) {
  loadStarted();
  wps = new SimpleWPS({
    process: "org.malleefowl.wms.animate.kml",
    raw: false,
    format: 'xml',
    onSuccess: function(xmlDoc) {
      //console.log(xmlDoc);
      kmlURL = $(xmlDoc).find("wps\\:Reference, Reference").first().attr('href');
      //console.log(kmlURL);
      loadFinished();
      downloadURL(kmlURL);
    },
  });
  wps.execute({
    service_url: layer.service,
    layer: layer.name,
    start: start_time,
    end: end_time,
    resolution: $("#select-resolution").val(),
    width: map.getSize().w,
    height: map.getSize().h,
    bbox: map.getExtent().toBBOX(),
  });  
}

var $idown;  // Keep it outside of the function, so it's initialized once.
function downloadURL(url) {
  if ($idown) {
    $idown.attr('src',url);
  } else {
    $idown = $('<iframe>', { id:'idown', src:url }).hide().appendTo('body');
  }
}

/*
function animateSlow(step) {
  if (step < 10) {
    $("#slider").slider( "value", step );
    setTimeout(function() {animate(step+1);}, 500);
  }
}
*/
