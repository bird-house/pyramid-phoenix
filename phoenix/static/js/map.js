var map, ia_wms, tds_wms;

function init() {
  var mapOptions = { maxResolution: 256/512, numZoomLevels: 11, fractionalZoom: true};
  //map = new OpenLayers.Map('map',mapOptions);
  map = new OpenLayers.Map('map');
  map.addControl(new OpenLayers.Control.LayerSwitcher());

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
}

function update_date() {
  var string = OpenLayers.Util.getElement('year').value + "-" +
    OpenLayers.Util.getElement('month').value + "-" +
    OpenLayers.Util.getElement('day').value + "T" +
    OpenLayers.Util.getElement('hour').value + ":" +
    OpenLayers.Util.getElement('minute').value + ":00";
  //ia_wms.mergeNewParams({'time':string});
  tds_wms.mergeNewParams({'time':string});
}

$(document).ready(function (e) {
  init();
});