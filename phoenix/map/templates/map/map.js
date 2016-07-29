var map = L.map('map', {
  zoom: 2,
  fullscreenControl: true,
% if dataset:
  timeDimension: true,
  timeDimensionOptions:{
    //times: "2001-01-16T12:00:00.000Z,2001-02-15T00:00:00.000Z,2001-03-16T12:00:00.000Z/2001-07-16T12:00:00.000Z/P30DT12H,2001-08-16T12:00:00.000Z/2001-12-16T12:00:00.000Z/P30DT12H,2002-01-16T12:00:00.000Z,2002-02-15T00:00:00.000Z,2002-03-16T12:00:00.000Z/2002-07-16T12:00:00.000Z/P30DT12H,2002-08-16T12:00:00.000Z/2002-12-16T12:00:00.000Z/P30DT12H,2003-01-16T12:00:00.000Z,2003-02-15T00:00:00.000Z,2003-03-16T12:00:00.000Z/2003-07-16T12:00:00.000Z/P30DT12H,2003-08-16T12:00:00.000Z/2003-12-16T12:00:00.000Z/P30DT12H,2004-01-16T12:00:00.000Z,2004-02-15T12:00:00.000Z,2004-03-16T12:00:00.000Z/2004-07-16T12:00:00.000Z/P30DT12H,2004-08-16T12:00:00.000Z/2004-12-16T12:00:00.000Z/P30DT12H,2005-01-16T12:00:00.000Z,2005-02-15T00:00:00.000Z,2005-03-16T12:00:00.000Z/2005-07-16T12:00:00.000Z/P30DT12H,2005-08-16T12:00:00.000Z/2005-12-16T12:00:00.000Z/P30DT12H"
    //timeInterval: "2001-01-16T12:00:00Z/2005-12-16T12:00:00Z",
    //period: "P1M"
  },
  timeDimensionControl: true,
  timeDimensionControlOptions:{
    //timeSteps: 12
  },
% endif    
  center: [20.0, 0.0],
});

L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
  attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'    
}).addTo(map);

% if dataset:
var testWMS = "/ows/proxy/wms?DATASET=${dataset}"
var testLayer = L.tileLayer.wms(testWMS, {
  layers: '${layers}',
  format: 'image/png',
  transparent: true,
  styles: '${styles}',
  attribution: '<a href="http://bird-house.github.io/">Birdhouse</a>'
});
var testTimeLayer = L.timeDimension.layer.wms(testLayer, {
  updateTimeDimension: true,
});
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
% endif

L.control.coordinates({
    position: "bottomright",
    decimals: 3,
    labelTemplateLat: "Latitude: {y}",
    labelTemplateLng: "Longitude: {x}",
    useDMS: true,
    enableUserInput: false
}).addTo(map);







