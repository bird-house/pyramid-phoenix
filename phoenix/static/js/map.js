var map,  wmsLayer, animateLayer;
var start_time, end_time;
var layerList;

function initMap() {
  var mapOptions = { maxResolution: 256/512, numZoomLevels: 11, fractionalZoom: true};
  //map = new OpenLayers.Map('map',mapOptions);
  map = new OpenLayers.Map('map');
  map.addControl(new OpenLayers.Control.LayerSwitcher());
  //map.addControl(new OpenLayers.Control.Attribution());
  //map.addControl(new OpenLayers.Control.Animate());

  var layer = new OpenLayers.Layer.WMS( "OpenLayers WMS",
                                        "http://vmap0.tiles.osgeo.org/wms/vmap0", 
                                        {layers: 'basic'} );
  map.addLayer(layer);

  // WMS tiled
  layer = new OpenLayers.Layer.WMS("World Map",
                                   "http://www2.demis.nl/wms/wms.ashx?WMS=WorldMap",
                                   {layers: '*', format: 'image/png'},
                                   {singleTile: false}
                                  );
  map.addLayer(layer);
  map.zoomToMaxExtent(); 

  initLayerList();
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
      $('select').html(output.join(''));

      $('select').change(function() {
        var layer = layerList[this.selectedIndex];
        showLayer(layer);
      });

      showLayer(layerList[0]);
    },
  });
  wps.execute();
}

function showLayer(layer) {
  if (wmsLayer != null) {
    map.removeLayer(wmsLayer);
  }
  wmsLayer = new OpenLayers.Layer.WMS(layer.title,
                                      layer.service,
                                      {layers: layer.name,
                                       transparent: true,
                                       format:'image/png',
                                       time: layer.timesteps[0]});
  
  map.addLayer(wmsLayer);
  wmsLayer.events.register('loadend', wmsLayer, function(evt){
    //map.zoomToExtent(new OpenLayers.Bounds(wmsLayer.getExtent()));
  }); 
  initTimeSlider(layer, wmsLayer);
}

function dateLabel(timestep) {
  return timestep.substring(0,16);
}

function initTimeSlider(layer, wmsLayer) {
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
      //tds_wms.setOpacity(ui.value / 10);
      var step = parseInt(ui.value);
      //console.log("step: " + step);
      $("#time").text(dateLabel(layer.timesteps[step]));
      wmsLayer.mergeNewParams({'time': layer.timesteps[step]});
    }
  });
  $("#time").text(dateLabel(layer.timesteps[0]));

  // prev button
  $("#prev").button({
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
    if (animateLayer != null) {
      map.removeLayer(animateLayer);
    }
  });
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
