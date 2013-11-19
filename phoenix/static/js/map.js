var map, ia_wms, tds_wms;

var timesteps = ["2006-01-01T12:00:00", "2006-01-02T12:00:00", "2006-01-03T12:00:00", 
                 "2006-01-04T12:00:00", "2006-01-05T12:00:00", "2006-01-06T12:00:00", 
                 "2006-01-07T12:00:00", "2006-01-08T12:00:00", "2006-01-09T12:00:00", 
                 "2006-01-10T12:00:00",];

function init() {
  var mapOptions = { maxResolution: 256/512, numZoomLevels: 11, fractionalZoom: true};
  //map = new OpenLayers.Map('map',mapOptions);
  map = new OpenLayers.Map('map');
  map.addControl(new OpenLayers.Control.LayerSwitcher());
  map.addControl(new OpenLayers.Control.Animate());

  var layer = new OpenLayers.Layer.WMS( "OpenLayers WMS",
                                        "http://vmap0.tiles.osgeo.org/wms/vmap0", {layers: 'basic'} );
  //map.addLayer(layer);

  // WMS tiled
  layer = new OpenLayers.Layer.WMS("World Map",
                                   "http://www2.demis.nl/wms/wms.ashx?WMS=WorldMap",
                                   {layers: '*', format: 'image/png'},
                                   {singleTile: false}
                                  );
  layer.setVisibility(true)
  map.addLayer(layer);


  // wms-t from tds
  tds_wms = new OpenLayers.Layer.WMS("TDS Test",
                                     "http://rockhopper.d.dkrz.de:8090/thredds/wms/test/cordex-eur-tas-pywpsInputT1Zaki.nc?",
                                     {layers:"tas",
                                      transparent:true,
                                      format:'image/png',
                                      time:"2006-01-01T12:00:00.000Z"});

 
  
  map.addLayer(tds_wms);
 
  //map.zoomToExtent(new OpenLayers.Bounds(-100.898437,22.148438,-78.398437,39.726563));
  map.zoomToMaxExtent();

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
    max: 9,
    step: 1,
    slide: function(e, ui) {
      var step = parseInt(ui.value);
      console.log("sliding ...");
      $("#time").text(timesteps[step]);
    },
    change: function(e, ui) {
      //tds_wms.setOpacity(ui.value / 10);
      var step = parseInt(ui.value);
      //console.log("step: " + step);
      console.log("time: " + timesteps[step]);
      $("#time").text(timesteps[step]);
      tds_wms.mergeNewParams({'time': timesteps[step]});
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
    if (current < 9 ) {
      $("#slider").slider( "value", current + 1 );
    }
  });;
  $("#play").button({
    icons: {
      primary: "ui-icon-gear",
      secondary: "ui-icon-triangle-1-s"
    },
    text: false,
  }).click(function( event ) {
    console.log('play button clicked');
  });;
}

$(document).ready(function (e) {
  init();
});