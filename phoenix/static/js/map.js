var map, animate_layer;
var start_time, end_time;

function initMap() {
  var mapOptions = { maxResolution: 256/512, numZoomLevels: 11, fractionalZoom: true};
  //map = new OpenLayers.Map('map',mapOptions);
  map = new OpenLayers.Map('map');
  map.addControl(new OpenLayers.Control.LayerSwitcher());
  //map.addControl(new OpenLayers.Control.Animate());

  var layer = new OpenLayers.Layer.WMS( "OpenLayers WMS",
                                        "http://vmap0.tiles.osgeo.org/wms/vmap0", {layers: 'basic'} );
  map.addLayer(layer);

  // WMS tiled
  layer = new OpenLayers.Layer.WMS("World Map",
                                   "http://www2.demis.nl/wms/wms.ashx?WMS=WorldMap",
                                   {layers: '*', format: 'image/png'},
                                   {singleTile: false}
                                  );
  map.addLayer(layer);
  map.zoomToMaxExtent(); 

  initLayer();
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
      $("#time").text(layer.timesteps[step]);
    },
    change: function(e, ui) {
      //tds_wms.setOpacity(ui.value / 10);
      var step = parseInt(ui.value);
      //console.log("step: " + step);
      $("#time").text(layer.timesteps[step]);
      layer.wms_layer.mergeNewParams({'time': layer.timesteps[step]});
    }
  });

  // prev button
  $("#prev").button({
    icons: {
      primary: "ui-icon-gear",
      secondary: "ui-icon-triangle-1-s"
    },
    text: false,
  }).click(function( event ) {
    console.log('prev button clicked');
    current = $("#slider").slider( "values", 0 );
    if (current > 0 ) {
      $("#slider").slider( "value", current - 1 );
    }
  });

  // next button
  $("#next").button({
    icons: {
      primary: "ui-icon-gear",
      secondary: "ui-icon-triangle-1-s"
    },
    text: false,
  }).click(function( event ) {
    console.log('next button clicked');
    current = $("#slider").slider( "values", 0 );
    if (current < max ) {
      $("#slider").slider( "value", current + 1 );
    }
  });
}

function initRangeSlider(layer) {
  var max = layer.timesteps.length - 1;

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
      
      console.log("sliding range ...");
      $( "#time-range" ).text( layer.timesteps[step0] + " - " + layer.timesteps[step1] );
      start_time = layer.timesteps[step0];
      end_time = layer.timesteps[step1];
    },
  });

  // play button
  $("#play").button({
    icons: {
      primary: "ui-icon-gear",
      secondary: "ui-icon-triangle-1-s"
    },
    text: false,
  }).click(function( event ) {
    console.log('play button clicked');
    animate(layer);
  });

  // stop button
  $("#stop").button({
    icons: {
      primary: "ui-icon-gear",
      secondary: "ui-icon-triangle-1-s"
    },
    text: false,
  }).click(function( event ) {
    console.log('stop button clicked');
    if (animate_layer != null) {
      map.removeLayer(animate_layer);
    }
  });
}

function initLayer() {
  wps = new SimpleWPS({
    process: "org.malleefowl.wms.layer",
    onSuccess: function(result) {
      console.log(result);
      $.each(result, function(index, layer) {
        wms_layer = new OpenLayers.Layer.WMS(layer.service_name + ":" + layer.title,
                                             layer.service,
                                             {layers: layer.name,
                                              transparent: true,
                                              format:'image/png',
                                              time: layer.timesteps[0]});
      
 
  
        wms_layer.setVisibility(false);
        map.addLayer(wms_layer);
        layer.wms_layer = wms_layer;
        wms_layer.events.register("visibilitychanged", layer, function() {
          if (layer.wms_layer.getVisibility()) {
            initTimeSlider(this);
            initRangeSlider(this);
          }
        });
      });
    },
  });
  wps.execute();
}

function animate(layer) {
  wps = new SimpleWPS({
    process: "org.malleefowl.wms.animate",
    raw: false,
    format: 'xml',
    onSuccess: function(xmlDoc) {
      //console.log(xmlDoc);
      var url = $(xmlDoc).find("wps\\:Reference, Reference").first().attr('href');
      console.log(url);

      animate_layer = new OpenLayers.Layer.Image(
        "Animation", url, map.getExtent(), map.getSize(), {
        isBaseLayer: false,
        alwaysInRange: true // Necessary to always draw the image
        });
      map.addLayer(animate_layer);
    },
  });
  wps.execute({
    service_url: layer.service,
    layer: layer.name,
    start: start_time,
    end: end_time,
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
