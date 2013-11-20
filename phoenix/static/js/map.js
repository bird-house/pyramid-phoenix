var map, tds_wms, animate_layer

function initMap() {
  var mapOptions = { maxResolution: 256/512, numZoomLevels: 11, fractionalZoom: true};
  //map = new OpenLayers.Map('map',mapOptions);
  map = new OpenLayers.Map('map');
  map.addControl(new OpenLayers.Control.LayerSwitcher());
  map.addControl(new OpenLayers.Control.Animate());

  var layer = new OpenLayers.Layer.WMS( "OpenLayers WMS",
                                        "http://vmap0.tiles.osgeo.org/wms/vmap0", {layers: 'basic'} );
  map.addLayer(layer);

  // WMS tiled
  layer = new OpenLayers.Layer.WMS("World Map",
                                   "http://www2.demis.nl/wms/wms.ashx?WMS=WorldMap",
                                   {layers: '*', format: 'image/png'},
                                   {singleTile: false}
                                  );
  layer.setVisibility(true)
  map.addLayer(layer);
  map.zoomToMaxExtent();

 
}

function initUI(layer) {
  var max = layer.timesteps.length - 1;

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
      tds_wms.mergeNewParams({'time': layer.timesteps[step]});
    }
  });
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
    url: "http://rockhopper.d.dkrz.de:8090/wps",
    process: "org.malleefowl.wms.layer",
    onSuccess: function(result) {
      console.log(result);
      layer = result[0]
      // wms-t from tds
      tds_wms = new OpenLayers.Layer.WMS(layer.title,
                                         "http://rockhopper.d.dkrz.de:8090/thredds/wms/test/cordex-eur-tas-pywpsInputT1Zaki.nc?",
                                         {layers: layer.name,
                                          transparent: true,
                                          format:'image/png',
                                          time: layer.timesteps[0]});
      
 
  
      map.addLayer(tds_wms);
 
      //map.zoomToExtent(new OpenLayers.Bounds(-100.898437,22.148438,-78.398437,39.726563));

      initUI(layer);
    },
  });
  wps.execute();
}

function animate(layer) {
  wps = new SimpleWPS({
    url: "http://rockhopper.d.dkrz.de:8090/wps",
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
    layer: layer.name,
    start: layer.timesteps[0],
    end: layer.timesteps[50],
    width: map.getSize().w,
    height: map.getSize().h,
    bbox: map.getExtent().toBBOX(),
  });  
}

function animateSlow(step) {
  if (step < 10) {
    $("#slider").slider( "value", step );
    setTimeout(function() {animate(step+1);}, 500);
  }
}

$(document).ready(function (e) {
  initMap();
  initLayer();
});