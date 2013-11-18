var map, ia_wms;

function init() {
  map = new OpenLayers.Map('map');
  var ol_wms = new OpenLayers.Layer.WMS( "OpenLayers WMS",
                                         "http://vmap0.tiles.osgeo.org/wms/vmap0", {layers: 'basic'} );
  var jpl_wms = new OpenLayers.Layer.WMS( "NASA Global Mosaic",
                                          "http://t1.hypercube.telascience.org/cgi-bin/landsat7", 
                                          {layers: "landsat7"});
  ia_wms = new OpenLayers.Layer.WMS("Nexrad","http://mesonet.agron.iastate.edu/cgi-bin/wms/nexrad/n0r-t.cgi?",
                                    {layers:"nexrad-n0r-wmst",
                                     transparent:true,
                                     format:'image/png',
                                     time:"2005-08-29T13:00:00Z"});

  map.addLayer(ol_wms);
  map.addLayer(jpl_wms);
  map.addLayer(ia_wms);
  map.addControl(new OpenLayers.Control.LayerSwitcher());
  map.zoomToExtent(new OpenLayers.Bounds(-100.898437,22.148438,-78.398437,39.726563));
  //map.zoomToMaxExtent();
}

function update_date() {
  var string = OpenLayers.Util.getElement('year').value + "-" +
    OpenLayers.Util.getElement('month').value + "-" +
    OpenLayers.Util.getElement('day').value + "T" +
    OpenLayers.Util.getElement('hour').value + ":" +
    OpenLayers.Util.getElement('minute').value + ":00";
  ia_wms.mergeNewParams({'time':string});
}

$(document).ready(function (e) {
  init();
});