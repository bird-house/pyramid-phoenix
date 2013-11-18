$(document).ready(function (e) {
  var map = new OpenLayers.Map('map');
  var wms = new OpenLayers.Layer.WMS( "OpenLayers WMS",
                                      "http://vmap0.tiles.osgeo.org/wms/vmap0", {layers: 'basic'} );
  map.addLayer(wms);
  map.zoomToMaxExtent();
});