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

function initMap() {
  initGlobe();
  initGlobeButtons();
  initOpacitySlider();
  initLayerList();
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

function addLayer(layer) {
  map.addLayer(layer);
  layer.events.register('loadstart', layer, function(evt){
    loadStarted();
  }); 
  layer.events.register('loadend', layer, function(evt){
    loadFinished();
  }); 
}

function initBaseLayer() {
  var baseLayer = null;
  /*
  baseLayer = new OpenLayers.Layer.WMS( 
    "Demis WMS",
    "http://www2.demis.nl/wms/wms.ashx?WMS=WorldMap",
    {layers:'Countries,Bathymetry,Topography,Hillshading,Coastlines,Builtup+areas,Waterbodies,Rivers,Streams,Railroads,Highways,Roads,Trails,Borders,Cities,Airports',
     format: 'image/png'});
  addLayer(baseLayer);
  */

  /*
  baseLayer = new OpenLayers.Layer.WMS( 
    "OpenLayers WMS",
    "http://labs.metacarta.com/wms-c/Basic.py?", {layers: 'basic'});
  addLayer(baseLayer);
  */

  baseLayer = new OpenLayers.Layer.WMS( 
    "Demis BlueMarble",
    "http://www2.demis.nl/wms/wms.ashx?WMS=BlueMarble" , 
    {layers: 'Earth Image,Borders,Coastlines'});
  addLayer(baseLayer);
}

function initGlobe(show3D) {
  show3D = show3D || false;

  if (map != null) {
    map.destroy();
  }

  //var mapOptions = { maxResolution: 256/512, numZoomLevels: 11, fractionalZoom: true};
  //map = new OpenLayers.Map('map',mapOptions);
  map = new OpenLayers.Map('map', { controls: [] });
  map.setupGlobe();
  layerSwitcher = new OpenLayers.Control.LayerSwitcher()
  //map.addControl(layerSwitcher);
  map.addControl(new OpenLayers.Control.Navigation());
  map.addControl(new OpenLayers.Control.PanZoom());
  //map.addControl(new OpenLayers.Control.Attribution());
  initBaseLayer();

  if (selectedLayer) {
    initWMSLayer(selectedLayer, selectedTimeIndex);
  } 
  if (animateURL) {
    //initAnimateLayer(animateURL);
  }
  map.finishGlobe();

  if (show3D) {
    map.show3D();
  }
  else {
    map.show2D();
  }
}

function initLayerList() {
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
  wps.execute();
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
  addLayer(wmsLayer);
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

function dateLabel(timestep) {
  return timestep.substring(0,16);
}

function initGlobeButtons() {
  // 2d button
  $("#2d").button({
    text: true,
  }).click(function( event ) {
    show2D();
  });

  // 3d button
  $("#3d").button({
    text: true,
  }).click(function( event ) {
    show3D();
  });
}

function show2D() {
  if (map.is3D) {
    map.show2D();
  }
}

function show3D() {
  if (!map.is3D) {
    initGlobe(true);
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
    console.log("ipdate layer");
    wmsLayer.setOpacity(opacity);
    if (redraw) wmsLayer.redraw();
  }
  if (animateLayer != null) {
    animateLayer.setOpacity(opacity);
    if (redraw) animateLayer.redraw();
  }

  $("#opacity-label").text("Overlay Opacity " + opacity*100 + "%");
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
      show2D();
      //tds_wms.setOpacity(ui.value / 10);
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
      show2D();
      $("#slider").slider( "value", current - 1 );
    }
  });

  // next button
  $("#next").button({
    text: false,
  }).click(function( event ) {
    //console.log('next button clicked');
    show2D();
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
            show2D();
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

function initAnimateLayer(imageURL) {
  animateLayer = new OpenLayers.Layer.Image(
    "Animation", imageURL, map.getExtent(), map.getSize(), {
      isBaseLayer: false,
      alwaysInRange: true, // Necessary to always draw the image
      opacity: opacity,
    });
  addLayer(animateLayer);
}

function animate(layer) {
  if (animateLayer != null) {
    map.removeLayer(animateLayer);
    animateLayer = null;
  }

  loadStarted();
  wps = new SimpleWPS({
    process: "org.malleefowl.wms.animate",
    raw: false,
    format: 'xml',
    onSuccess: function(xmlDoc) {
      //console.log(xmlDoc);
      animateURL = $(xmlDoc).find("wps\\:Reference, Reference").first().attr('href');
      initAnimateLayer(animateURL);
      loadFinished();
    },
  });
  wps.execute({
    service_url: layer.service,
    layer: layer.name,
    start: start_time,
    end: end_time,
    resolution: $("#select-resolution").val(),
    delay: $("#delay").val(),
    width: map.getSize().w,
    height: map.getSize().h,
    bbox: map.getExtent().toBBOX(),
  });  
}

/*
function animateSlow(step) {
  if (step < 10) {
    $("#slider").slider( "value", step );
    setTimeout(function() {animate(step+1);}, 500);
  }
}
*/
