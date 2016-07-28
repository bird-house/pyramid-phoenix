var map = L.map('map', {
  zoom: 2,
  fullscreenControl: true,
  timeDimension: true,
  timeDimensionOptions:{
    timeInterval: "2001-01-16T12:00:00Z/2005-12-16T12:00:00Z",
    period: "P1M"
  },
  timeDimensionControl: true,
  timeDimensionControlOptions:{
    timeSteps: 12
  },    
  center: [20.0, 0.0],
});

L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
  attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'    
}).addTo(map);

var testWMS = "http://localhost:8080/ncWMS2/wms?DATASET=${dataset}"
//var testWMS = "/ows/proxy/wms?DATASET=outputs/hummingbird/output-3d059bc0-5033-11e6-9fa2-af0ebe9e921e.nc"
var testLayer = L.tileLayer.wms(testWMS, {
  layers: '${layers}',
  format: 'image/png',
  transparent: true,
  styles: '${styles}',
  attribution: '<a href="http://bird-house.github.io/">Birdhouse</a>'
});
var testTimeLayer = L.timeDimension.layer.wms(testLayer);
testTimeLayer.addTo(map);

var testLegend = L.control({
    position: 'topright'
});
testLegend.onAdd = function(map) {
    var src = testWMS + "&SERVICE=WMS&VERSION=1.3.0&REQUEST=GetLegendGraphic&LAYERS=${layers}&STYLES=${styles}&PALETTE=default&HEIGHT=300";
    var div = L.DomUtil.create('div', 'info legend');
    div.innerHTML +=
        '<img src="' + src + '" alt="legend">';
    return div;
};
testLegend.addTo(map);

L.control.coordinates({
    position: "bottomright",
    decimals: 3,
    labelTemplateLat: "Latitude: {y}",
    labelTemplateLng: "Longitude: {x}",
    useDMS: true,
    enableUserInput: false
}).addTo(map);







